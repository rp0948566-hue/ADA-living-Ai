import indexer


def test_index_search_and_secrets(tmp_path, monkeypatch):
    root = tmp_path / "proj"; root.mkdir()
    (root / "app.py").write_text("def compute_total(items):\n    return sum(items)\n")
    (root / ".env").write_text("API_KEY=supersecretvalue\n")
    (root / "keys.pem").write_text("-----BEGIN-----")
    (root / "node_modules").mkdir(); (root / "node_modules" / "lib.js").write_text("compute_total hidden")
    db = tmp_path / "i.db"
    monkeypatch.setattr(indexer, "DB", db)
    r = indexer.refresh([root], db)
    assert r["total"] == 1  # only app.py: .env, .pem and node_modules are skipped
    assert "app.py:1" in indexer.search_code("compute_total")
    assert indexer.search_code("supersecretvalue").startswith("no indexed match")
    (root / "app.py").write_text("def other():\n    pass\n")
    indexer.refresh([root], db)
    assert "no indexed match" in indexer.search_code("compute_total")


def test_read_file_refuses_secrets(tmp_path):
    f = tmp_path / ".env"; f.write_text("A=1")
    assert indexer.read_file(str(f)).startswith("refused")
