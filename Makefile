.PHONY: install test run web lint clean

# ─── Installation ──────────────────────────────────────────────────────────────
install:
	pip install -e .
install-dev:
	pip install -e ".[dev]"
install-all:
	pip install -e ".[dev,web,astro]"

# ─── Testing ───────────────────────────────────────────────────────────────────
test:
	pytest -v

test-cov:
	pytest -v --cov=xuanzhao

# ─── Run CLI ───────────────────────────────────────────────────────────────────
run:
	python xuanzhao.py analyze --birth "2005-06-09 11:50" --location 呼和浩特 --gender male

# ─── Web server ────────────────────────────────────────────────────────────────
web:
	python app.py

# ─── Lint ──────────────────────────────────────────────────────────────────────
lint:
	@echo "=== Python syntax check ==="
	@python -m py_compile xuanzhao.py 2>&1 || true
	@python -m py_compile app.py 2>&1 || true
	@find . -name '*.py' -not -path './__pycache__/*' -not -path './*/__pycache__/*' \
		-not -path './.git/*' -not -path './.github/*' \
		-exec sh -c 'python -m py_compile "$$1" 2>&1 || true' _ {} \;
	@echo "=== Done ==="

# ─── Clean ─────────────────────────────────────────────────────────────────────
clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleaned."
