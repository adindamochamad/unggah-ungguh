.PHONY: up down logs seed test eval lint

up:
	docker compose up --build -d
	@echo "Waiting for wiki on :8080 …"
	@for i in $$(seq 1 90); do \
		if curl -sf http://localhost:8080/index.php >/dev/null; then echo "wiki is up"; exit 0; fi; \
		sleep 3; \
	done; echo "timeout waiting for mediawiki"; exit 1

down:
	docker compose down

logs:
	docker compose logs -f --tail=100

seed:
	docker compose exec -T mediawiki php /seed/seed.php

test:
	docker compose exec -T -e PYTHONPATH=/app service pytest -q

eval:
	docker compose exec -T service python -m app.eval

lint:
	docker compose exec -T service ruff check app tests
