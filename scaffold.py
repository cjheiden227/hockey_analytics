
def scaffold():
    """Builds folder paths safely to prevent directory access violations."""
    print("[1/4] Constructing development pathways...")
    for folder in DIRS:
        full_path = os.path.join(PROJECT_ROOT, folder)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
            print(f" -> Created directory: {folder}")
    print("Scaffolding complete.")

def resolve_dependencies():
    """Forces pip optimization using binary fallbacks to stop driver errors."""
    print("\n[2/4] Syncing explicit core library packages (including Psycopg drivers)...")
    packages = [
        "pandas", "numpy", "matplotlib", "seaborn", 
        "requests", "beautifulsoup4", "sqlalchemy", 
        "psycopg2-binary", "psycopg", "psycopg-binary", "jupyterlab"
    ]
    
    # Upgrade pip engine installer tool
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    
    # Batch download analytics stack libraries
    subprocess.run([sys.executable, "-m", "pip", "install"] + packages, check=True)
    print("Core package resolution verification complete.")

def write_notebook():
    """Generates the workspace notebook using native JSON compiling to avoid NotJSONErrors."""
    print("\n[3/4] Initializing clean Jupyter exploratory notebook...")
    notebook_path = os.path.join(PROJECT_ROOT, "notebooks", "exploratory_analysis.ipynb")
    
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
                    "from sqlalchemy import create_engine\n\n",
                    f"engine = create_engine('postgresql+psycopg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}')\n",
                    "print('Analytic engine handshake initialized safely using native Psycopg driver.')"
                ]
            }
        ],
        "metadata": {"language_info": {"name": "python"}},
        "nbformat": 4,
        "nbformat_minor": 2
    }
    
    with open(notebook_path, "w", encoding="utf-8") as f:
        json.dump(nb_struct, f, indent=2)
    print(" -> Deployed clean notebook file: notebooks/exploratory_analysis.ipynb")

def initialize_database():
    """Deploys table schema scripts directly into local PostgreSQL instance."""
    print("\n[4/4] Executing structural table initialization routines...")
    
    # Target string configuration mapping utilizing the native psycopg v3 driver format
    db_url = f"postgresql+psycopg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(db_url)
    
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
                clean_statement = statement.strip()
                if clean_statement:
                    connection.execute(text(clean_statement))
        print(" -> Relational schemas successfully loaded to PostgreSQL server.")
    except Exception as e:
        print(f" -> Execution warning: {e}")
        print(" -> Verify local service status and base credentials matching config parameters.")