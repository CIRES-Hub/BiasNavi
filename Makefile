.PHONY: setup, run, stop-db, start-db, clean-db

# First time setup
setup:
	echo "Installing dependencies"
	pip install -r ./requirements.txt
	echo "Setting up a database"
	docker compose -f docker-compose.yml up -d --wait
	docker exec -i biasnavi-postgres psql -U postgres < scripts/create_db.sql
	echo "You're all set!"

run:
	python main.py

stop-db:
	docker compose -f docker-compose.yml stop

clean-db:
	docker compose -f docker-compose.yml down --rmi all

start-db:
	docker compose -f docker-compose.yml up -d --wait
