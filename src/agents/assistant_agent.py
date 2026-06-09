from agent_framework import Agent, SkillsProvider, create_harness_agent
from agent_framework.foundry import FoundryChatClient
from agent_framework.hyperlight import HyperlightCodeActProvider

from agents.hyperlight_skill_runner import make_hyperlight_script_runner

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

    codeact = HyperlightCodeActProvider(
        approval_mode="never_require",
    )

    # Skills provider with the Hyperlight-backed script runner. Built explicitly
    # (instead of skills_paths=) so we can attach a runner — without one,
    # file-based skill scripts are not executable. Reuse the provider's sandbox
    # surface so skill scripts see the same tools as the model's execute_code.
    skills = SkillsProvider.from_paths(
        "./skills",
        script_runner=make_hyperlight_script_runner(codeact._execute_code_tool),
    )

    agent = create_harness_agent(
        client,
        max_context_window_tokens=200_000,
        max_output_tokens=32_000,
        name="contract_assistant",
        description="A versatile assistant for contract analysis and comparison.",
        agent_instructions=(
            "You are a versatile legal assistant capable of comparing clauses, analyzing clauses, "
            "comparing entire contracts and rewriting contracts based on user requests. "
            "Use the appropriate tool based on the user's needs."
        ),
        skills_provider=skills,
        context_providers=[codeact],
        tools=tools,
    )
    return agent
