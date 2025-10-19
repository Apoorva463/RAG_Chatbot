"""
FastAPI REST API for Favorites Management
Handles user favorites storage and retrieval
"""

import sqlite3
import json
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
import os

# Pydantic models
class Song(BaseModel):
    title: str
    author: str
    genre: str
    mood: str
    year: int

class FavoriteRequest(BaseModel):
    song: Song

class FavoriteResponse(BaseModel):
    user_id: str
    favorites: List[Song]
    total_count: int

class FavoritesAPI:
    def __init__(self, db_path: str = "favorites.db"):
        """Initialize the favorites API with SQLite database"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for favorites"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create favorites table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                song_title TEXT NOT NULL,
                song_author TEXT NOT NULL,
                song_genre TEXT NOT NULL,
                song_mood TEXT NOT NULL,
                song_year INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, song_title, song_author)
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"Database initialized at {self.db_path}")
    
    def add_favorite(self, user_id: str, song: Song) -> bool:
        """Add a song to user's favorites"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO favorites 
                (user_id, song_title, song_author, song_genre, song_mood, song_year)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, song.title, song.author, song.genre, song.mood, song.year))
            
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
        finally:
            conn.close()
    
    def get_favorites(self, user_id: str) -> List[Song]:
        """Get all favorites for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT song_title, song_author, song_genre, song_mood, song_year
                FROM favorites 
                WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (user_id,))
            
            rows = cursor.fetchall()
            favorites = []
            
            for row in rows:
                song = Song(
                    title=row[0],
                    author=row[1],
                    genre=row[2],
                    mood=row[3],
                    year=row[4]
                )
                favorites.append(song)
            
            return favorites
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            conn.close()
    
    def remove_favorite(self, user_id: str, song_title: str, song_author: str) -> bool:
        """Remove a song from user's favorites"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                DELETE FROM favorites 
                WHERE user_id = ? AND song_title = ? AND song_author = ?
            ''', (user_id, song_title, song_author))
            
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
        finally:
            conn.close()
    
    def clear_favorites(self, user_id: str) -> bool:
        """Clear all favorites for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM favorites WHERE user_id = ?', (user_id,))
            conn.commit()
            return cursor.rowcount >= 0
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
        finally:
            conn.close()
    
    def get_favorites_count(self, user_id: str) -> int:
        """Get count of favorites for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM favorites WHERE user_id = ?', (user_id,))
            count = cursor.fetchone()[0]
            return count
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return 0
        finally:
            conn.close()
    
    def get_all_users_favorites(self) -> Dict[str, List[Song]]:
        """Get favorites for all users (for analytics)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT user_id, song_title, song_author, song_genre, song_mood, song_year
                FROM favorites 
                ORDER BY user_id, created_at DESC
            ''')
            
            rows = cursor.fetchall()
            user_favorites = {}
            
            for row in rows:
                user_id = row[0]
                song = Song(
                    title=row[1],
                    author=row[2],
                    genre=row[3],
                    mood=row[4],
                    year=row[5]
                )
                
                if user_id not in user_favorites:
                    user_favorites[user_id] = []
                user_favorites[user_id].append(song)
            
            return user_favorites
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return {}
        finally:
            conn.close()

# Initialize FastAPI app
app = FastAPI(title="Favorites API", description="API for managing user song favorites")

# Initialize favorites API
favorites_api = FavoritesAPI()

@app.post("/favorites/{user_id}", response_model=Dict[str, str])
async def add_favorite(user_id: str, favorite_request: FavoriteRequest):
    """Add a song to user's favorites"""
    success = favorites_api.add_favorite(user_id, favorite_request.song)
    
    if success:
        return {"message": f"Song '{favorite_request.song.title}' added to favorites for user {user_id}"}
    else:
        raise HTTPException(status_code=400, detail="Failed to add favorite or song already exists")

@app.get("/favorites/{user_id}", response_model=FavoriteResponse)
async def get_favorites(user_id: str):
    """Get all favorites for a user"""
    favorites = favorites_api.get_favorites(user_id)
    
    return FavoriteResponse(
        user_id=user_id,
        favorites=favorites,
        total_count=len(favorites)
    )

@app.delete("/favorites/{user_id}")
async def remove_favorite(user_id: str, song_title: str, song_author: str):
    """Remove a specific song from user's favorites"""
    success = favorites_api.remove_favorite(user_id, song_title, song_author)
    
    if success:
        return {"message": f"Song '{song_title}' by {song_author} removed from favorites"}
    else:
        raise HTTPException(status_code=404, detail="Favorite not found")

@app.delete("/favorites/{user_id}/clear")
async def clear_favorites(user_id: str):
    """Clear all favorites for a user"""
    success = favorites_api.clear_favorites(user_id)
    
    if success:
        return {"message": f"All favorites cleared for user {user_id}"}
    else:
        raise HTTPException(status_code=500, detail="Failed to clear favorites")

@app.get("/favorites/{user_id}/count")
async def get_favorites_count(user_id: str):
    """Get count of favorites for a user"""
    count = favorites_api.get_favorites_count(user_id)
    return {"user_id": user_id, "favorites_count": count}

@app.get("/favorites/analytics/all")
async def get_all_favorites_analytics():
    """Get favorites analytics for all users"""
    all_favorites = favorites_api.get_all_users_favorites()
    
    analytics = {
        "total_users": len(all_favorites),
        "total_favorites": sum(len(favorites) for favorites in all_favorites.values()),
        "user_favorites": all_favorites
    }
    
    return analytics

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
