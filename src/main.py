import os
import chainlit as cl

from typing import Annotated, List
from dotenv import load_dotenv
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import DefaultAzureCredential

from processors.document_processor import DocumentProcessor
from agents.assistant_agent import get_assistant_agent

load_dotenv(override=True)

processor = DocumentProcessor()

def create_client() -> FoundryChatClient:
    """Create the shared Foundry chat client used by every agent."""
    return FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["FOUNDRY_MODEL"],
        credential=DefaultAzureCredential(),
    )


async def create_chainlit_file_download(
    filename: Annotated[str, "The file name of the generated document to offer for download."],
) -> str:
    """Create a Chainlit file download link for the given filename."""
    elements = [
        cl.File(
            name=filename,
            path=filename,
            display="inline",
        )
    ]
    await cl.Message(content="File Link", elements=elements).send()
    return f"A download link for '{filename}' has been shared with the user."


@cl.set_starters
async def set_starters():
    """Set starters for the chat."""
    return [
        cl.Starter(
            label="Compare Clause",
            message="Compare the IP clause of the uploaded contract with the template clause and highlight any differences."
        ),
        cl.Starter(
            label="Analyze Clause",
            message="Analyze the retainer clause of the uploaded contract and suggest improvements."
        ),
        cl.Starter(
            label="Compare Contract",
            message="Compare the uploaded contract with the template contract and highlight any differences."
        ),
        cl.Starter(
            label="Rewrite Contract",
            message="Analyze the uploaded contract with the template contract and rewrite a new version of the contract that combines the best clauses from both contracts into a new contract."
        )
    ]


@cl.on_chat_start
async def on_chat_start():
    """Initialize the chat with an agent and a conversation session."""
    client = create_client()
    agent = get_assistant_agent(
        processor,
        client,
        extra_tools=[create_chainlit_file_download],
    )

    # Sessions/conversation state are explicit in Agent Framework: create one and
    # reuse it across turns so the agent retains history.
    session = agent.create_session()

    cl.user_session.set("agent", agent)
    cl.user_session.set("session", session)


@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming messages."""
    agent = cl.user_session.get("agent")
    session = cl.user_session.get("session")

    # Check if there are files attached to the message
    if message.elements:
        await cl.Message(content="Processing your uploaded files...").send()
        await process_files(message.elements)
        
    current_filename = cl.user_session.get("filename", "sample-01.pdf")  # Hardcoded for debugging
    print(f"Using {current_filename} as the current filename for agent tools.")
    
    # On the first turn, tell the agent which files to retrieve with its tools.
    if not cl.user_session.get("initialized", False):
        user_message = f"Using your plugins to retrieve the template contract and the uploaded contract using the file name: {current_filename}, perform the following: {message.content}"
        cl.user_session.set("initialized", True)
    else:
        user_message = message.content

    await stream_agent_response(
        agent=agent,
        session=session,
        answer=cl.Message(content=""),
        message=user_message,
    )


async def stream_agent_response(agent: Agent, session, answer: cl.Message, message: str):
    """Stream the agent's response."""

    async for update in agent.run(message, session=session, stream=True):
        if update.text:
            await answer.stream_token(update.text)

    await answer.send()


async def process_files(files: List[cl.File]):
    """Process uploaded files."""

    if len(files) > 1:
        await cl.Message(content="Only one file is supported at a time. Please upload a single file.").send()
        return

    filename = ""
    for file in files:
        filename = file.name

        await cl.Message(content=f"Ingesting file: {filename} ...").send()

        with open(file.path, "rb") as f:
            stats = await processor.process_file(f, filename)
            print(f"Processed {stats.clauses_created} clauses from {stats.total_pages} pages")

        # Send confirmation back to user
        await cl.Message(content=f"Successfully ingested file: {filename}").send()
        cl.user_session.set("filename", filename)


if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)
