import os
import random
import pygame

class MusicPlayer:
    def __init__(self, mood="calm"):
        """
        mood: "calm" or "crazy"
        Expects folders:
          music/
            calm/
            crazy/
        """
        pygame.mixer.init()
        self.base_dir = os.path.join(os.path.dirname(__file__), "music")
        self.set_mood(mood)

    def set_mood(self, mood):
        mood = mood.lower()
        if mood not in ("calm", "crazy"):
            raise ValueError(f"Invalid mood '{mood}'. Use 'calm' or 'crazy'.")
        self.mood = mood
        self.mood_dir = os.path.join(self.base_dir, mood)
        if not os.path.isdir(self.mood_dir):
            raise FileNotFoundError(f"No folder for mood '{mood}' at {self.mood_dir}")

    def play_random_song(self):
        # Grab all .mp3/.wav files in the mood folder
        songs = [f for f in os.listdir(self.mood_dir)
                 if f.lower().endswith((".mp3", ".wav"))]
        if not songs:
            print(f"[!] No songs found in {self.mood_dir}")
            return

        song = random.choice(songs)
        full_path = os.path.join(self.mood_dir, song)
        pygame.mixer.music.load(full_path)
        pygame.mixer.music.play()
        print(f"[♪] Now playing ({self.mood}): {song}")
