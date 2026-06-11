import asyncio
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Optional

#from __future__ import annotations
from agent_framework import FileSkill, FileSkillScript

import warnings
warnings.filterwarnings("ignore", message=r"\[SKILLS\].*", category=FutureWarning)

class ScriptRunnerService:
    """Service for running file-based skill scripts as local Python subprocesses.

    Provided as a local alternative to the Hyperlight sandbox runner for demos
    and offline use. Use :meth:`as_script_runner` to obtain a callable that
    matches the agent_framework ``SkillScriptRunner`` protocol.
    """

    def __init__(self, timeout: int = 30, python_executable: Optional[str] = None):
        """Create the service.

        Args:
            timeout: Maximum seconds a script may run before it is killed.
            python_executable: Python interpreter used to run scripts. Defaults
                to the interpreter running this process.
        """
        self.timeout = timeout
        self.python_executable = python_executable or sys.executable

    def as_script_runner(self) -> Callable[..., Any]:
        """Return a callable matching the ``SkillScriptRunner`` protocol.

        Returns:
            An async callable ``(skill, script, args) -> str`` suitable for
            passing as the ``script_runner`` of an agent.
        """
        return self.run_script

    async def run_script(
        self, skill: FileSkill, script: FileSkillScript, args: dict[str, Any] | list[str] | None = None
    ) -> str:
        """Run a skill script as a local Python subprocess.

        Uses ``FileSkillScript.full_path`` as the script path, converts ``args``
        to CLI arguments, and returns the captured output.

        Args:
            skill: The file-based skill that owns the script.
            script: The file-based script to run.
            args: Optional arguments. A ``list[str]`` is forwarded as positional
                CLI arguments. Any other non-``None`` type raises ``TypeError`` —
                file-based scripts expect positional arguments as a list of strings.

        Returns:
            The combined stdout/stderr output, or an error message.

        Raises:
            TypeError: If ``args`` is not a ``list[str]`` or ``None``, or if any
                list element is not a string.
        """
        script_path = Path(script.full_path)
        if not script_path.is_file():
            return f"Error: Script file not found: {script_path}"

        cmd = self._build_command(script_path, args)

        try:
            result = await asyncio.to_thread(
                subprocess.run,
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=str(script_path.parent),
            )
            return self._format_output(result)
        except subprocess.TimeoutExpired:
            return f"Error: Script '{script.name}' timed out after {self.timeout} seconds."
        except OSError as e:
            return f"Error: Failed to execute script '{script.name}': {e}"

    def _build_command(
        self, script_path: Path, args: dict[str, Any] | list[str] | None
    ) -> list[str]:
        """Build the subprocess command line for a script and its arguments."""
        cmd = [self.python_executable, str(script_path)]
        if isinstance(args, list):
            for item in args:
                if not isinstance(item, str):
                    raise TypeError(
                        f"File-based skill scripts only accept string CLI arguments "
                        f"but received a {type(item).__name__}. "
                        f"All array elements must be strings."
                    )
            cmd.extend(args)
        elif args is not None:
            raise TypeError(
                f"Expected a list of CLI arguments but received {type(args).__name__}. "
                f"File-based skill scripts expect positional arguments as a list of strings."
            )
        return cmd

    @staticmethod
    def _format_output(result: subprocess.CompletedProcess) -> str:
        """Combine stdout/stderr and exit status into a single output string."""
        output = result.stdout
        if result.stderr:
            output += f"\nStderr:\n{result.stderr}"
        if result.returncode != 0:
            output += f"\nScript exited with code {result.returncode}"
        return output.strip() or "(no output)"
