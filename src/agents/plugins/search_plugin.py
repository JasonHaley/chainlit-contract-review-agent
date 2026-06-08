from typing import Annotated


class SearchPlugin:
    """A plugin for searching contract clauses.

    Each public method is exposed to the agent as a tool. The method name is the
    tool name, the docstring is the tool description, and Annotated parameter hints
    become the tool's argument descriptions.
    """

    def __init__(self, search_service):
        self.search_service = search_service

    def get_tools(self):
        """Return the bound methods to register as agent tools."""
        return [
            self.search_for_clause_in_uploaded_contract,
            self.search_for_clause_in_template_contract,
            self.get_all_clauses_in_uploaded_contract,
            self.get_all_clauses_in_template_contract,
        ]

    async def search_for_clause_in_uploaded_contract(
        self,
        search_text: Annotated[str, "The text describing the clause to search for."],
        uploaded_contract_filename: Annotated[str, "The file name of the uploaded contract."],
    ) -> str:
        """Search for a clause in the uploaded contract based on the search text and return the full clause text."""
        print(f"Searching for clause in uploaded contract: {uploaded_contract_filename} with search text: {search_text}")

        uploaded_contract_clause = await self.search_service.search_single_hybrid(query=search_text, filter=f"doc_id eq '{uploaded_contract_filename}'")
        if not uploaded_contract_clause:
            return "No matching clause found in the uploaded document. Please try another clause."
        return uploaded_contract_clause.text_full

    async def search_for_clause_in_template_contract(
        self,
        search_text: Annotated[str, "The text describing the clause to search for."],
    ) -> str:
        """Search for a clause in the template based on the search text and return the full clause text."""
        print(f"Searching for clause in template with search text: {search_text}")

        template_clause = await self.search_service.search_single_hybrid(query=search_text, filter=f"is_template eq true")
        if not template_clause:
            return "No matching clause found in the template. Please try another clause."
        return template_clause.text_full

    async def get_all_clauses_in_uploaded_contract(
        self,
        uploaded_contract_filename: Annotated[str, "The file name of the uploaded contract."],
    ) -> str:
        """Get the complete uploaded contract."""
        print(f"Getting all clauses in uploaded contract: {uploaded_contract_filename}")

        clauses = await self.search_service.search_clauses_by_filter(filter=f"doc_id eq '{uploaded_contract_filename}'")
        if not clauses or len(clauses) == 0:
            return "No clauses found in the uploaded document."
        return "\n\n".join([f"{clause.clause_type}: {clause.text_full}" for clause in clauses])

    async def get_all_clauses_in_template_contract(self) -> str:
        """Get the complete template contract."""
        print(f"Getting all clauses in template contract")

        clauses = await self.search_service.search_clauses_by_filter(filter=f"is_template eq true")
        if not clauses or len(clauses) == 0:
            return "No clauses found in the template."
        return "\n\n".join([f"{clause.clause_type}: {clause.text_full}" for clause in clauses])
