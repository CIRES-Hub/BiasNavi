.PHONY: setup create-db run stop-db start-db clean-db check-docker

# Internal: Check if current user has access to Docker
check-docker:
	@echo "[INFO] Checking Docker access (docker version)..."
	@docker version > /dev/null 2>&1 || ( \
		echo "[✘] You do NOT have permission to access Docker."; \
		echo "→ Run: sudo usermod -aG docker $$USER && newgrp docker"; \
		echo "→ Or use sudo: sudo make <target>"; \
		exit 1 \
	)
	@echo "[✔] Docker access confirmed."


# First time setup
setup: check-docker
	@echo "Setting up a database..."
	docker compose -f docker-compose.yml up -d --wait
	@echo "You're all set!"

create-db:
	docker exec -i biasnavi-postgres psql -U postgres < scripts/create_db.sql

run:
	python main.py

stop-db:
	docker compose -f docker-compose.yml stop

clean-db:
	docker compose -f docker-compose.yml down --rmi all

start-db:
	docker compose -f docker-compose.yml up -d --wait
