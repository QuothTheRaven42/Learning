import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from collections import defaultdict

client_id = "604c5db4edfb465b9be5ae0617f2006d"
client_secret = "3a721f517c334a278d4fa24df41e718e"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=client_id,
    client_secret=client_secret
))

# tracks = []
# results = sp.search(q="artist:Harry Styles", type="track", limit=10)
# for track in results["tracks"]["items"]:
#     tracks.append({
#         "name": track["name"],
#         "album": track["album"]["name"],
#         "release_date": track["album"]["release_date"],
#         "duration_ms": track["duration_ms"],
#         "explicit": track["explicit"]
#     })
#
# # this block starts at the leftmost column, not indented
# tracks_sorted = sorted(tracks, key=lambda x: x["duration_ms"], reverse=True)
#
# print("Harry Styles songs by length (longest to shortest):")
# print("-" * 50)
# for track in tracks_sorted:
#     duration_seconds = track["duration_ms"] // 1000
#     minutes = duration_seconds // 60
#     seconds = duration_seconds % 60
#     print(f"{track['name']} - {minutes}:{seconds:02d} ({track['album']})")
#
# avg_ms = sum(t["duration_ms"] for t in tracks) / len(tracks)
# avg_min = (avg_ms // 1000) // 60
# avg_sec = (avg_ms // 1000) % 60
# print(f"\nAverage song length: {int(avg_min)}:{int(avg_sec):02d}")

# search each album separately
tracks = []
albums = ["Harry Styles", "Fine Line", "Harry's House"]

for album_name in albums:
    results = sp.search(q=f"album:{album_name} artist:Harry Styles", type="track", limit=10)
    for track in results["tracks"]["items"]:
        artists = [a["name"] for a in track["artists"]]
        if "Harry Styles" in artists:
            tracks.append({
                "name": track["name"],
                "album": track["album"]["name"],
                "release_date": track["album"]["release_date"],
                "duration_ms": track["duration_ms"],
                "explicit": track["explicit"]
            })

# remove duplicates
seen = set()
unique_tracks = []
for track in tracks:
    if track["name"] not in seen:
        seen.add(track["name"])
        unique_tracks.append(track)

tracks = unique_tracks
print(f"Unique tracks: {len(tracks)}")

# sort by duration
tracks_sorted = sorted(tracks, key=lambda x: x["duration_ms"], reverse=True)

print("\nHarry Styles songs by length (longest to shortest):")
print("-" * 50)
for track in tracks_sorted:
    duration_seconds = track["duration_ms"] // 1000
    minutes = duration_seconds // 60
    seconds = duration_seconds % 60
    print(f"{track['name']} - {minutes}:{seconds:02d} ({track['album']})")

# overall average
avg_ms = sum(t["duration_ms"] for t in tracks) / len(tracks)
avg_min = int((avg_ms // 1000) // 60)
avg_sec = int((avg_ms // 1000) % 60)
print(f"\nOverall average song length: {avg_min}:{avg_sec:02d}")

# average per album
album_durations = defaultdict(list)
for track in tracks:
    album_durations[track["album"]].append(track["duration_ms"])

print("\nAverage song length by album:")
print("-" * 50)
for album, durations in album_durations.items():
    avg_ms = sum(durations) / len(durations)
    avg_min = int((avg_ms // 1000) // 60)
    avg_sec = int((avg_ms // 1000) % 60)
    print(f"{album}: {avg_min}:{avg_sec:02d} average ({len(durations)} tracks)")