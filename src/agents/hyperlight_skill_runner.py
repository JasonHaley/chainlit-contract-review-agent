"""Adapter that runs file-based skill scripts inside a Hyperlight sandbox.

`HyperlightCodeActProvider` is a ContextProvider (it gives the *model* an
`execute_code` tool); it is not a `SkillScriptRunner`. A script runner is just a
callable ``(skill, script, args) -> Any``. This module builds such a callable on
top of `HyperlightExecuteCodeTool` so that the `.py` scripts shipped inside
``skills/<name>/scripts/`` run in the same sandbox as the CodeAct surface.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from agent_framework.hyperlight import HyperlightExecuteCodeTool


def make_hyperlight_script_runner(
    execute_tool: HyperlightExecuteCodeTool,
) -> Callable[..., Any]:
    """Build a SkillScriptRunner backed by a Hyperlight sandbox.

    Args:
        execute_tool: The sandbox surface used to run code. Reuse the same
            instance the CodeAct provider uses so skill scripts see the same
            provider-owned tools, file mounts, and allowed domains.

    Returns:
        An async callable matching the `SkillScriptRunner` protocol.
    """

    async def run_script(skill, script, args: dict | list | None = None) -> Any:
        # The sandbox is isolated, so we read the script source on the host and
        # ship it as a code string rather than relying on the file existing in
        # the guest filesystem.
        source = await _read_source(script.full_path)

        # Make the runner's `args` available to the script inside the sandbox as
        # a module-level `args` variable (json round-trip keeps it a safe literal).
        preamble = (
            "import json\n"
            f"args = json.loads({json.dumps(json.dumps(args))})\n"
        )

        code = f"{preamble}\n{source}"

        # skip_parsing=True returns the sandbox's raw value (list[Content]) so we
        # don't double-wrap it; the SkillsProvider serialises it for the model.
        return await execute_tool.invoke(arguments={"code": code}, skip_parsing=True)

    return run_script


async def _read_source(full_path: str) -> str:
    import asyncio

    return await asyncio.to_thread(Path(full_path).read_text, encoding="utf-8")
