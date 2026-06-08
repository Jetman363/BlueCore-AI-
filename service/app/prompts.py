from pathlib import Path

from app.settings import settings

_PROMPT_CACHE: dict[str, str] = {}


def _prompts_root() -> Path:
    configured = Path(settings.prompts_dir)
    if configured.is_dir():
        return configured
    # Local development: repo prompts/ adjacent to service/
    local = Path(__file__).resolve().parents[2] / "prompts"
    if local.is_dir():
        return local
    return configured


def load_prompt(name: str) -> str:
    if name in _PROMPT_CACHE:
        return _PROMPT_CACHE[name]
    path = _prompts_root() / f"{name}.md"
    if not path.is_file():
        raise FileNotFoundError(f"Prompt not found: {path}")
    text = path.read_text(encoding="utf-8")
    _PROMPT_CACHE[name] = text
    return text


def assistant_system_prompt() -> str:
    return load_prompt("law-enforcement-assistant")


def threat_assessment_system_prompt() -> str:
    return load_prompt("threat-assessment-module")
