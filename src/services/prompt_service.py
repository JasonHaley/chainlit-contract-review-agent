import json
import os
import pathlib

class PromptyService:

    PROMPTS_DIRECTORY = pathlib.Path(__file__).parent.parent / "prompts"

    def load_prompt(self, path: str):
        # Prompts are plain text files; normalize any legacy .prompty extension to .txt.
        filename = pathlib.Path(path).with_suffix(".txt").name
        return self.load(self.PROMPTS_DIRECTORY, filename)

    def load_tools(self, path: str):
        return json.loads(open(self.PROMPTS_DIRECTORY / path).read())

    def render_prompt(self, prompt: str, data: dict) -> str:
        """Substitute {key} placeholders in a plain-text prompt with values from data.

        Only the keys present in data are replaced, so unrelated braces in the
        prompt (for example, JSON examples) are left untouched.
        """
        rendered = prompt
        for key, value in data.items():
            rendered = rendered.replace("{" + key + "}", str(value))
        return rendered

    def render_prompt_as_string(self, prompt: str, data: dict) -> str:
        return self.render_prompt(prompt, data)

    def load(self, path: str, filename: str) -> str:
        file_path = os.path.join(path, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        return text