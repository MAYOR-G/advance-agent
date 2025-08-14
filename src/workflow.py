from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage 
from src.models import ResearchState, CompanyAnalysis, CompanyInfo
from src.firecrawl import FirecrawlService
from src.prompts import DeveloperToolsPrompts

class Workflow:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.1)
        self.firecrawl_service = FirecrawlService()
        self.prompts = DeveloperToolsPrompts()
        self.workflow = self._build_workflow()
        
    def _build_workflow(self):
        graph = StateGraph(ResearchState)
        graph.add_node("extract_tools", self._extract_tools_step)
        graph.add_node("research", self._research_step)
        graph.add_node("analyze", self._analyze_step)
        graph.set_entry_point("extract_tools")
        graph.add_edge("extract_tools", "research")
        graph.add_edge("research", "analyze")
        graph.add_edge("analyze", END)
        return graph.compile()
    
    def _extract_tools_step(self, state: ResearchState) -> Dict[str, Any]:
        print(f"Extracting tools for query: {state.query}")
        
        article_query = f"{state.query} tools comparison for best alternative"
        search_results = self.firecrawl_service.search_companies(article_query,  num_results=5)
        
        all_content = ""
        for result in search_results:
            url = result.get("url", "")
            scraped = self.firecrawl_service.scrape(url)
            if scraped:
                all_content += scraped.markdown[:1000] + "\n\n"
                
        messages = [
            SystemMessage(content=self.prompts.TOOL_EXTRACTION_SYSTEM),
            HumanMessage(content=self.prompts.tool_extraction_user(state.query, all_content))
        ]
        
        try:
            response = self.llm.invoke(messages)
            tool_names = [
                name.strip()
                for name in response.content.strip().split("\n")
                if name.strip()
            ]
            
            print(f"Extracted tools: {', '.join(tool_names[:5])}")
            return {
                "extracted_tools": tool_names,
                
            }
        except Exception as e:
            print(f"Error during tool extraction: {e}")
            return {
                "extracted_tools": [],
            }
            
            
    
    def _analyze_company_content(self, company_name: str, content: str) -> CompanyAnalysis:
        structured_llm = self.llm.with_structured_output(CompanyAnalysis)
        messages = [
            SystemMessage(content=self.prompts.TOOL_ANALYSIS_SYSTEM),
            HumanMessage(content=self.prompts.tool_analysis_user(company_name, content))
        ]
    
        try:
            analysis = structured_llm.invoke(messages)
            return analysis
        except Exception as e:
            print(e)
            return CompanyAnalysis(
                pricing_model="Unknown",
                is_open_source=None,
                tech_stack=[],
                description="failed to analyze",
                api_available=None,
                language_support=[],
                integration_capabilities=[]
            )    
    def _research_step(self, state: ResearchState) -> Dict[str, Any]:
       extracted_tools = getattr(state, "extracted_tools", [])
       
       if not extracted_tools: 
            print("No tools extracted, running extraction step...")
            search_results = self.firecrawl_service.search_companies(state.query, num_results=5)
            tool_names = [
                result.get("metadata", {}).get("title", "unknown")
                for result in search_results.data
            ]
       else:
            tool_names = extracted_tools[:5]  # Limit to top 5 tools
            
       print(f"Researching {len(tool_names)} tools: {', '.join(tool_names)}")
       
       companies = []
       for tool in tool_names:
           tools_search_result = self.firecrawl_service.search_companies(tool, num_results=1)
           
           if tools_search_result:
               result = tools_search_result.data[0]
               url = result.get("url", "")
               
               company = CompanyInfo(
                   name=tool,
                   description=result.get("markdown", ""),
                    website=url,
                    tech_stack=[],
                    competitors=[],
                    
               )
               
               scraped = self.firecrawl_service.scrape_company_page(url)
               if scraped:
                   content = scraped.markdown[:2500]  # Limit to first 2500 characters
                   analysis = self._analyze_company_content(company.name, content)
                   
                   company.pricing_model = analysis.pricing_model
                   company.is_open_source = analysis.is_open_source
                   company.tech_stack = analysis.tech_stack
                   company.description = analysis.description
                   company.api_available = analysis.api_available
                   company.language_support = analysis.language_support
                   company.integration_capabilities = analysis.integration_capabilities
                        
               companies.append(company)
         
       return {
            "companies": companies}  
    
    def _analyze_step(self, state: ResearchState) -> Dict[str, Any]:
        print("Analyzing companies...")
        
        company_data = ", ".join([
            company.model_dump_json() for company in state.companies 
        ])
        
        messages = [
            SystemMessage(content=self.prompts.RECOMMENDATIONS_SYSTEM),
            HumanMessage(content=self.prompts.recommendations_user(state.query, company_data))
        ]
        
        response = self.llm.invoke(messages)
        return {
            "analysis": response.content()
        }
        
    def run(self, query: str) -> ResearchState:
        initial_state = ResearchState(query=query)
        state = self.workflow.invoke(initial_state)
        
        return ResearchState(**state)
