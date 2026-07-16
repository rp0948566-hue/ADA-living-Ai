import sys, os
sys.path.insert(0, os.getcwd())
from Jarvis_youtube_music import play_youtube_song_sync

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python tools/test_youtube_play.py "song name"')
        sys.exit(1)
    song = sys.argv[1]
    print('Attempting to play:', song)
    res = play_youtube_song_sync(song)
    print('Result:', res)
