# ─────────────────────────────────────────────────────────────
#  Lakoli Admin API — Makefile
#  Utilise config/dev.py pour le développement local
# ─────────────────────────────────────────────────────────────

DJANGO_SETTINGS = --settings=config.dev
PYTHON = .venv/bin/python
PIP    = .venv/bin/pip

.PHONY: help setup run migrations migrate createsuperuser worker test clean \
        setupwin runwin migrationswin migratewin createsuperuserwin workerwin cleanwin

# ─────────────────────────────────────────────────────────────
#  AIDE
# ─────────────────────────────────────────────────────────────

help:
	@echo ""
	@echo "╔══════════════════════════════════════════════════════╗"
	@echo "║         Lakoli Admin API — Commandes Make            ║"
	@echo "╠══════════════════════════════════════════════════════╣"
	@echo "║  🐧 LINUX / MAC                                      ║"
	@echo "║    make setup            Créer le venv + installer   ║"
	@echo "║    make run              Lancer le serveur Django     ║"
	@echo "║    make migrations       Créer les migrations         ║"
	@echo "║    make migrate          Appliquer les migrations     ║"
	@echo "║    make createsuperuser  Créer un superutilisateur    ║"
	@echo "║    make worker           Lancer le worker Celery      ║"
	@echo "║    make test             Lancer les tests             ║"
	@echo "║    make clean            Supprimer venv + pycache     ║"
	@echo "╠══════════════════════════════════════════════════════╣"
	@echo "║  🪟 WINDOWS (cmd)                                    ║"
	@echo "║    make setupwin            Créer le venv + installer ║"
	@echo "║    make runwin              Lancer le serveur Django  ║"
	@echo "║    make migrationswin       Créer les migrations      ║"
	@echo "║    make migratewin          Appliquer les migrations  ║"
	@echo "║    make createsuperuserwin  Créer un superutilisateur ║"
	@echo "║    make workerwin           Lancer le worker Celery   ║"
	@echo "║    make cleanwin            Supprimer venv + pycache  ║"
	@echo "╚══════════════════════════════════════════════════════╝"
	@echo ""

# ─────────────────────────────────────────────────────────────
#  🐧 LINUX / MAC
# ─────────────────────────────────────────────────────────────

setup:
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements/development.txt

run:
	$(PYTHON) src/manage.py runserver $(DJANGO_SETTINGS)

migrations:
	$(PYTHON) src/manage.py makemigrations $(DJANGO_SETTINGS)

migrate:
	$(PYTHON) src/manage.py migrate $(DJANGO_SETTINGS)

createsuperuser:
	$(PYTHON) src/manage.py createsuperuser $(DJANGO_SETTINGS)

worker:
	@echo "Lancement du worker Celery..."
	cd src && DJANGO_SETTINGS_MODULE=config.dev ../$(PYTHON) -m celery -A config worker --loglevel=info

test:
	$(PYTHON) -m pytest src/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .venv

# ─────────────────────────────────────────────────────────────
#  🪟 WINDOWS (cmd)
# ─────────────────────────────────────────────────────────────

setupwin:
	python -m venv .venv
	.venv\Scripts\pip install --upgrade pip
	.venv\Scripts\pip install -r requirements\development.txt

runwin:
	.venv\Scripts\python src\manage.py runserver --settings=config.dev

migrationswin:
	.venv\Scripts\python src\manage.py makemigrations --settings=config.dev

migratewin:
	.venv\Scripts\python src\manage.py migrate --settings=config.dev

createsuperuserwin:
	.venv\Scripts\python src\manage.py createsuperuser --settings=config.dev

workerwin:
	cd src && set DJANGO_SETTINGS_MODULE=config.dev && ..\\.venv\\Scripts\\celery -A config worker --loglevel=info

cleanwin:
	rmdir /s /q .venv
	for /d /r . %d in (__pycache__) do @if exist "%d" rmdir /s /q "%d"