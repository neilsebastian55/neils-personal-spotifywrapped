import os
import pandas as pd

from spotify_auth import get_spotify_client



def fetch_top_tracks(sp, limit = 50, time_range = "medium_term"):
    """
    get the top tracks for a given time range.
    time_range: 'short_term', 'medium_term, or 'long_term'
    """
    
    results = sp.current_user_top_tracks(limit = limit, time_range = time_range)
    rows = []

    for item in results['items']:
        rows.append({
            "track_id": item["id"],
            "track_name": item["name"],
            "album_name": item["album"]["name"],
            "artist_name": ",".join(a["name"] for a in item["artists"]),
            "time_range": time_range,
            "popularity": item.get("popularity", None),
        })

    return pd.DataFrame(rows)



def fetch_recently_played(sp, limit = 50):
    """
    Get the user's recently played tracks (up to 50).
    Includes timestamps so we can build the time map later
    """
    results = sp.current_user_recently_played(limit = limit)
    rows = []

    for item in results['items']:
        track = item["track"]
        rows.append({
            "track_id": track["id"],
            "track_name": track["name"],
            "artist_name": ",".join(a["name"] for a in track["artists"]),
            "album_name": track["album"]["name"],
            "played_at": item["played_at"],
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df["played_at"] = pd.to_datetime(df["played_at"])
    return df



def fetch_audio_features(sp, track_ids, batch_size=100):
    """
    Fetches audio features for track IDs in batches.
    Temporarily wrapped in try/except because Spotify's audio-features 
    endpoint is returning 403 errors for this account/app.
    
    Until permissions/scopes are fixed, we skip the request and return
    an empty DataFrame so the rest of the pipeline still works.
    """
    import pandas as pd

    all_features = []

    for i in range(0, len(track_ids), batch_size):
        batch = track_ids[i:i + batch_size]
        try:
            features = sp.audio_features(batch)
            # Only append valid results
            for f in features:
                if f is not None:
                    all_features.append(f)

        except Exception as e:
            # 🟡 TEMPORARY BEHAVIOR:
            # We are seeing repeated 403 Forbidden errors from Spotify,
            # so instead of crashing the whole script, we skip audio features.
            print(f"[WARN] Skipping audio features for batch due to error: {e}")
            print("Returning partial data collected so far (may be empty).")
            return pd.DataFrame(all_features)

    return pd.DataFrame(all_features)



if __name__ == "__main__":
    sp = get_spotify_client()

    # --- Top tracks ---
    time_ranges = ["short_term", "medium_term", "long_term"]
    dfs = []

    for t in time_ranges:
        print(f"Fetching top tracks for {t}...")
        df_t = fetch_top_tracks(sp, limit=50, time_range=t)
        dfs.append(df_t)

    top_tracks_all = pd.concat(dfs, ignore_index=True)
    top_tracks_all.to_csv("data/top_tracks_all.csv", index=False)
    print("Saved 150 top tracks to data/top_tracks_all.csv")

    # --- Recently played ---
    recent_df = fetch_recently_played(sp, limit=50)
    recent_df.to_csv("data/recently_played.csv", index=False)
    print("Saved 50 recently played tracks to data/recently_played.csv")

    # --- TEMP: skip audio features due to 403 errors ---
    print("Skipping audio-features fetch for now (Spotify API returns 403).")
