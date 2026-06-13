from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient

from agents.plugins.doc_gen_plugin import DocGenPlugin
from agents.plugins.search_plugin import SearchPlugin
from processors.document_processor import DocumentProcessor

def get_rewrite_analysis_agent(processor: DocumentProcessor, client: FoundryChatClient) -> Agent:

    rewrite_analysis_prompt = processor.prompt_service.load_prompt("rewrite_analysis.txt")
    instructions = processor.prompt_service.render_prompt_as_string(rewrite_analysis_prompt, {
        "desired_terms": processor.desired_terms,
    })

    agent = Agent(
        client,
        instructions,
        name="rewrite_analysis_contract",
        description="Analyze the contracts to prepare to rewrite the contract.",
        tools=SearchPlugin(processor.search_service).get_tools(),
    )
    return agent

def get_rewrite_contract_agent(processor: DocumentProcessor, client: FoundryChatClient) -> Agent:

    rewrite_rewrite_prompt = processor.prompt_service.load_prompt("rewrite_contract.txt")
    instructions = processor.prompt_service.render_prompt_as_string(rewrite_rewrite_prompt, {
        "desired_terms": processor.desired_terms,
    })

    agent = Agent(
        client,
        instructions,
        name="rewrite_rewrite_contract",
        description="Rewrite the contract using the style of the uploaded contract, rewrite the entire document based on the template and desired terms using the word document plugin to create a word file.",
        tools=DocGenPlugin(processor.document_service).get_tools(),
    )
    return agent
