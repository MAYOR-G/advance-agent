class DeveloperToolsPrompts:
    """Collection of enhanced prompts for analyzing and recommending developer tools and technologies"""

    # Tool extraction prompts
    TOOL_EXTRACTION_SYSTEM = """You are an AI research assistant specializing in developer technologies. 
                            Your task is to extract the names of actual tools, libraries, platforms, or services that developers can use.
                            Focus on tangible products developers can directly apply in their work — avoid abstract concepts, methodologies, or general features."""

    @staticmethod
    def tool_extraction_user(query: str, content: str) -> str:
        return f"""Query: {query}
                Article Content: {content}

                From the content above, extract a list of actual developer tools, libraries, platforms, or services that are relevant to the topic: "{query}".

                Rules:
                - Only include real, usable products (e.g., SDKs, APIs, platforms, dev tools)
                - Avoid general concepts like "cloud", "CI/CD", or "frontend framework"
                - Include both open-source and commercial tools
                - Choose the 5 most relevant to developers
                - Return one tool name per line with no numbering or description

                Example format:
                Supabase
                PlanetScale
                Railway
                Appwrite
                Nhost"""

    # Company/Tool analysis prompts
    TOOL_ANALYSIS_SYSTEM = """You are an expert analyst reviewing developer tools and platforms. 
                            Focus only on aspects that matter to developers: programming languages, frameworks, SDKs, APIs, integrations, and development workflows.
                            Avoid business/marketing details unless they directly impact the developer experience."""

    @staticmethod
    def tool_analysis_user(company_name: str, content: str) -> str:
        return f"""Company/Tool: {company_name}
                Website Content: {content[:2500]}

                From the content above, analyze and extract key developer-focused information in the following structure:

                - pricing_model: One of "Free", "Freemium", "Paid", "Enterprise", or "Unknown"
                - is_open_source: true if open source, false if proprietary, null if unclear
                - tech_stack: List of technologies used or supported (e.g., React, PostgreSQL, Docker, GraphQL)
                - description: A short one-sentence explanation of what this tool offers to developers
                - api_available: true if APIs, SDKs, or programmatic interfaces are available
                - language_support: List of explicitly supported languages (e.g., JavaScript, Python, Go)
                - integration_capabilities: List of tools/services it integrates with (e.g., GitHub, AWS, VS Code, Slack)

                Only include information directly relevant to developers and engineering workflows."""

    # Recommendation prompts
    RECOMMENDATIONS_SYSTEM = """You are a senior software engineer helping developers choose the best tools for their needs. 
                            Keep your advice short, clear, and focused on technical advantages, pricing, and integration support.
                            Your goal is to guide developers to the best fit tool with just a few high-impact sentences."""

    @staticmethod
    def recommendations_user(query: str, company_data: str) -> str:
        return f"""Developer Query: {query}
                Tools/Technologies Analyzed: {company_data}

                Based on the tools above, write a brief recommendation (3-4 sentences) that includes:
                - The best tool for the use case and why
                - Any key cost or pricing consideration
                - A core technical advantage or integration benefit

                Keep it concise, technical, and actionable."""


