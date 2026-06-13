from typing import Annotated


class DocGenPlugin:
    """A plugin for generating Word documents.

    Each public method is exposed to the agent as a tool. The method name is the
    tool name, the docstring is the tool description, and Annotated parameter hints
    become the tool's argument descriptions.
    """

    def __init__(self, document_service):
        self.document_service = document_service

    def get_tools(self):
        """Return the bound methods to register as agent tools."""
        return [
            self.create_document,
            self.add_section,
            self.add_heading,
            self.add_paragraph,
        ]

    async def create_document(
        self,
        filename: Annotated[str, "The file name for the new Word document."],
        title: Annotated[str, "The document title metadata."],
        author: Annotated[str, "The document author metadata."],
    ) -> str:
        """Create a new Word document with optional metadata."""
        print(f"Creating document: {filename}, title: {title}, author: {author}")

        return await self.document_service.create_document(filename, title, author)

    async def add_section(
        self,
        filename: Annotated[str, "The file name of the Word document to modify."],
        heading: Annotated[str, "The heading text for the section."],
        heading_level: Annotated[int, "The heading level (1-9)."],
        paragraphs: Annotated[list[str], "The paragraphs to add under the heading."],
    ) -> str:
        """Adds a heading and list of strings as paragraphs to a Word document."""
        print(f"Adding section to document: {filename}, heading: {heading}, paragraphs: {paragraphs}")

        await self.document_service.add_heading(filename, heading, heading_level)
        for paragraph in paragraphs:
            await self.document_service.add_paragraph(filename, paragraph)

        return f"Section '{heading}' added to document '{filename}'."

    async def add_heading(
        self,
        filename: Annotated[str, "The file name of the Word document to modify."],
        text: Annotated[str, "The heading text."],
        level: Annotated[int, "The heading level (1-9)."],
    ) -> str:
        """Add a heading to a Word document."""
        print(f"Adding heading to document: {filename}, text: {text}, level: {level}")

        return await self.document_service.add_heading(filename, text, level)

    async def add_paragraph(
        self,
        filename: Annotated[str, "The file name of the Word document to modify."],
        text: Annotated[str, "The paragraph text."],
    ) -> str:
        """Add a paragraph to a Word document."""
        print(f"Adding paragraph to document: {filename}, text: {text}")

        return await self.document_service.add_paragraph(filename, text)
