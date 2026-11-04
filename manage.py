#!/usr/bin/env python
import os
import sys
import json
import argparse
import subprocess
from sqlalchemy import text

# Import your unified settings and engine from config.py
from config.config import settings, engine

DIRS = ["config", "data/raw", "data/processed", "database", "notebooks", "src"]


def cmd_setup(args):
    """Creates project directories, installs dependencies, writes the notebook, and initializes DB tables."""
    print("=== [1/4] Constructing development pathways ===")
    for folder in DIRS:
        full_path = settings.BASE_DIR / folder
        if not full_path.exists():
            full_path.mkdir(parents=True, exist_ok=True)
            print(f" -> Created directory: {folder}")
    print("Scaffolding complete.\n")

    print("=== [2/4] Syncing explicit core library packages ===")
    packages = [
        "pandas", "numpy", "matplotlib", "seaborn", 
        "requests", "beautifulsoup4", "sqlalchemy", 
        "psycopg2-binary", "psycopg", "psycopg-binary", "jupyterlab", "pydantic-settings", "nhl-api-py"
    ]
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run([sys.executable, "-m", "pip", "install"] + packages, check=True)
    print("Core package resolution verification complete.\n")

    print("=== [3/4] Initializing clean Jupyter exploratory notebook ===")
    notebook_path = settings.BASE_DIR / "notebooks" / "exploratory_analysis.ipynb"
    nb_struct = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Hockey Analytics Explorer\n",
                    "Validated environment playground for compiling Corsi calculations and testing database execution scripts."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "import os\n",
                    "import numpy as np\n",
                    "import pandas as pd\n",
                    "from config.config import engine, settings\n\n",
                    "print(f'Connected to database via URL: {settings.database_url}')\n",
                    "print('Analytic engine handshake initialized safely.')"
                ]
            }
        ],
        "metadata": {"language_info": {"name": "python"}},
        "nbformat": 4,
        "nbformat_minor": 2
    }
    with open(notebook_path, "w", encoding="utf-8") as f:
        json.dump(nb_struct, f, indent=2)
    print(f" -> Deployed clean notebook file: {notebook_path}\n")

    print("=== [4/4] Executing structural table initialization routines ===")
    schema_sql = """
    CREATE TABLE IF NOT EXISTS teams (
        team_id VARCHAR(3) PRIMARY KEY,
        franchise_name VARCHAR(50) NOT NULL,
        division VARCHAR(20),
        conference VARCHAR(20)
    );

    CREATE TABLE IF NOT EXISTS players (
        player_id INT PRIMARY KEY,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        primary_position VARCHAR(2)
    );

    CREATE TABLE IF NOT EXISTS games (
        game_id INT PRIMARY KEY,
        season_id INT NOT NULL,
        game_date DATE NOT NULL,
        home_team_id VARCHAR(3) REFERENCES teams(team_id),
        away_team_id VARCHAR(3) REFERENCES teams(team_id),
        home_score INT NOT NULL,
        away_score INT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS player_game_box_scores (
        game_id INT REFERENCES games(game_id),
        player_id INT REFERENCES players(player_id),
        team_id VARCHAR(3) REFERENCES teams(team_id),
        time_on_ice INTERVAL NOT NULL,
        goals INT DEFAULT 0,
        assists INT DEFAULT 0,
        points INT DEFAULT 0,
        plus_minus INT DEFAULT 0,
        penalty_minutes INT DEFAULT 0,
        shots_on_goal INT DEFAULT 0,
        hits INT DEFAULT 0,
        blocked_shots INT DEFAULT 0,
        giveaways INT DEFAULT 0,
        takeaways INT DEFAULT 0,
        faceoff_wins INT DEFAULT 0,
        faceoff_attempts INT DEFAULT 0,
        corsi_for_even_strength INT DEFAULT 0,
        corsi_against_even_strength INT DEFAULT 0,
        fenwick_for_even_strength INT DEFAULT 0,
        fenwick_against_even_strength INT DEFAULT 0,
        PRIMARY KEY (game_id, player_id)
    );

    CREATE INDEX IF NOT EXISTS idx_box_scores_player ON player_game_box_scores(player_id);
    CREATE INDEX IF NOT EXISTS idx_box_scores_game ON player_game_box_scores(game_id);
    """
    try:
        with engine.begin() as connection:
            for statement in schema_sql.split(";"):
                clean_stmt = statement.strip()
                if clean_stmt:
                    connection.execute(text(clean_stmt))
        print(" -> Relational schemas successfully loaded to PostgreSQL server.")
    except Exception as e:
        print(f" -> Execution warning: {e}")


def cmd_fetch(args):
    """Placeholder command for running your data ingestion scripts."""
    print("Running data ingestion pipeline...")
    # Example: from src.fetch_red_wings import run_fetcher; run_fetcher()
    print("Data ingestion routine complete.")


def main():
    parser = argparse.ArgumentParser(description="Hockey Analytics Pipeline Management CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # python manage.py setup
    parser_setup = subparsers.add_parser("setup", help="Initialize directories, dependencies, notebook, and database tables.")
    parser_setup.set_defaults(func=cmd_setup)

    # python manage.py fetch
    parser_fetch = subparsers.add_parser("fetch", help="Run raw play-by-play data ingestion scripts.")
    parser_fetch.set_defaults(func=cmd_fetch)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()