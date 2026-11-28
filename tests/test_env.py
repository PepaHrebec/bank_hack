import os

from run import load_env


def test_load_env_reads_keys_and_skips_comments(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_MODEL", raising=False)
    env = tmp_path / ".env"
    env.write_text(
        "# OpenRouter\n"
        "\n"
        "OPENROUTER_API_KEY=sk-or-abc=123\n"
        'OPENROUTER_MODEL = "anthropic/some-model"\n'
    )
    load_env(env)
    assert os.environ["OPENROUTER_API_KEY"] == "sk-or-abc=123"
    assert os.environ["OPENROUTER_MODEL"] == "anthropic/some-model"


def test_load_env_keeps_variables_already_set(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENROUTER_MODEL", "from-shell")
    env = tmp_path / ".env"
    env.write_text("OPENROUTER_MODEL=from-file\n")
    load_env(env)
    assert os.environ["OPENROUTER_MODEL"] == "from-shell"


def test_load_env_without_file_does_nothing(tmp_path):
    load_env(tmp_path / "missing.env")
