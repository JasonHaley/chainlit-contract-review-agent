from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient

from agents.analyze_clause_agent import get_analyze_clause_agent
from agents.compare_clause_agent import get_compare_clause_agent
from agents.compare_contract_agent import get_compare_contract_agent
from agents.rewrite_contract_agent import get_rewrite_analysis_agent, get_rewrite_contract_agent

from processors.document_processor import DocumentProcessor

def get_assistant_agent(processor: DocumentProcessor, client: FoundryChatClient, extra_tools=None) -> Agent:

    compare_clause_agent = get_compare_clause_agent(processor, client)
    analyze_clause_agent = get_analyze_clause_agent(processor, client)
    compare_contract_agent = get_compare_contract_agent(processor, client)
    analysis_agent = get_rewrite_analysis_agent(processor, client)
    rewrite_agent = get_rewrite_contract_agent(processor, client)

    # Sub-agents are exposed to the assistant as callable tools (agents-as-tools).
    tools = [
        compare_clause_agent.as_tool(
            name="compare_clause",
            description="Compare a specific clause of the uploaded contract with the template clause and highlight differences.",
        ),
        analyze_clause_agent.as_tool(
            name="analyze_clause",
            description="Analyze a specific clause in the uploaded contract and suggest improvements based on best practices.",
        ),
        compare_contract_agent.as_tool(
            name="compare_contract",
            description="Compare the entire uploaded contract with the template and highlight any differences.",
        ),
        analysis_agent.as_tool(
            name="rewrite_analysis_contract",
            description="Analyze the contracts to prepare to rewrite the contract.",
        ),
        rewrite_agent.as_tool(
            name="rewrite_rewrite_contract",
            description="Rewrite the contract based on the template and desired terms, producing a Word document.",
        ),
    ]
    if extra_tools:
        tools.extend(extra_tools)

    agent = Agent(
        client,
        "You are a versatile legal assistant capable of comparing clauses, analyzing clauses, comparing entire contracts and rewriting contracts based on user requests. Use the appropriate tool based on the user's needs.",
        name="contract_assistant",
        description="A versatile assistant for contract analysis and comparison.",
        tools=tools,
    )
    return agent
