from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient

from agents.plugins.search_plugin import SearchPlugin
from processors.document_processor import DocumentProcessor

def get_compare_clause_agent(processor: DocumentProcessor, client: FoundryChatClient) -> Agent:
    compare_clause = processor.prompt_service.load_prompt("compare_clause.txt")
    instructions = processor.prompt_service.render_prompt_as_string(compare_clause, {
        "desired_terms": processor.desired_terms,
    })

    agent = Agent(
        client,
        instructions,
        name="compare_clause",
        description="Compare the entire uploaded contract with the template and highlight any differences.",
        tools=SearchPlugin(processor.search_service).get_tools(),
    )
    return agent
