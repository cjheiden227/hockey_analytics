import os
import pandas as pd
import nhlpy
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables for secure database connection
load_dotenv()
DB_USER = os.getenv("DB_USER", "hockey_db")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "hockey_stats")

# Initialize database engine
db_url = f"postgresql+psycopg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(db_url)

def fetch_red_wings_history():
    from nhlpy import schedule
    # Define the last 3 seasons (NHL seasons are formatted asYYYYYYYY, e.g., 20232024 for 2023-24)
    seasons = ["20232024", "20242025", "20252026"]
    team_abbr = "DET"
    
    all_schedules = []
    
    print(f"Initializing data pull for the Detroit Red Wings ({team_abbr})...")
    
    for season in seasons:
        print(f" -> Fetching schedule and game data for season: {season[:4]}-{season[4:]}")
        try:
            # Fetch the club schedule for the specified season
            all_games = schedule.Schedule()
            
            # Extract games data (adjusting based on nhlpy JSON schema return structure)
            if "games" in all_games:
                for game in all_games["games"]:
                    game_record = {
                        "game_id": game.get("id"),
                        "season_id": int(season),
                        "game_date": game.get("gameDate"),
                        "home_team_id": game.get("homeTeam", {}.get("abbrev")),
                        "away_team_id": game.get("awayTeam", {}.get("abbrev")),
                        "home_score": game.get("homeTeam", {}.get("score", 0)),
                        "away_score": game.get("awayTeam", {}.get("score", 0))
                    }
                    all_schedules.append(game_record)
        except Exception as e:
            print(f"    Warning: Could not pull season {season}: {e}")

    if all_schedules:
        games_df = pd.DataFrame(all_schedules)
        # Drop duplicates if any overlap occurs
        games_df.drop_duplicates(subset=["game_id"], inplace=True)
        
        print(f"\nSuccessfully collected {len(games_df)} games across the last 3 seasons.")
        
        # Load games into PostgreSQL database
        try:
            games_df.to_sql('games', con=engine, if_exists='append', index=False, method='multi')
            print(" -> Games successfully loaded into PostgreSQL database table 'games'.")
        except Exception as db_err:
            print(f" -> Database insertion error: {db_err}")
    else:
        print("No game records retrieved. Please check API connectivity or season parameters.")

if __name__ == "__main__":
    fetch_red_wings_history()