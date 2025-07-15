import mysql.connector

class Scores:
    def __init__(self, host="localhost", user="root", password="", database="flappybird"):
        """Initialize the leaderboard with a MySQL database."""
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """Create the scores table if it doesn't exist."""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INT AUTO_INCREMENT PRIMARY KEY,
            player_name VARCHAR(50) NOT NULL,
            score INT NOT NULL
        );
        """)
        self.conn.commit()

    def add_score(self, player_name, score):
        """Add a new score to the scores table."""
        try:
            self.cursor.execute("""
            INSERT INTO scores (player_name, score)
            VALUES (%s, %s);
            """, (player_name, score))
            self.conn.commit()
        except Exception as e:
            print(f"Error adding score: {e}")

    def get_top_scores(self, limit=10):
        """Retrieve the top scores from the scores table."""
        try:
            self.cursor.execute("""
            SELECT player_name, MAX(score) as max_score
            FROM scores
            GROUP BY player_name
            ORDER BY max_score DESC
            LIMIT %s;
            """, (limit,))
            return [(row[0], row[1]) for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching leaderboard: {e}")
            return []

    def close(self):
        """Close the database connection."""
        try:
            self.cursor.close()
            self.conn.close()
        except Exception as e:
            print(f"Error closing connection: {e}")
