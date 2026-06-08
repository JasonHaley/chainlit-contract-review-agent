from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient

from agents.plugins.search_plugin import SearchPlugin
from processors.document_processor import DocumentProcessor

def get_analyze_clause_agent(processor: DocumentProcessor, client: FoundryChatClient) -> Agent:

    analyze_prompt = processor.prompt_service.load_prompt("analyze_clause.txt")
    instructions = processor.prompt_service.render_prompt_as_string(analyze_prompt, {
        "desired_terms": processor.desired_terms,
    })

    agent = Agent(
        client,
        instructions,
        name="analyze_clause",
        description="Analyze a specific clause in the uploaded contract and suggest improvements based on best practices.",
        tools=SearchPlugin(processor.search_service).get_tools(),
    )
    return agent
