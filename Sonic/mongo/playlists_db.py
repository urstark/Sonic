import typing
from Sonic.core.mongo import mongodb

playlistdb = mongodb.playlists

async def create_playlist(user_id: int, name: str, is_public: bool = False):
    doc = {
        "user_id": user_id,
        "name": name,
        "is_public": is_public,
        "tracks": []
    }
    await playlistdb.insert_one(doc)

async def delete_playlist(user_id: int, name: str) -> bool:
    result = await playlistdb.delete_one({"user_id": user_id, "name": name})
    return result.deleted_count > 0

async def get_playlist(user_id: int, name: str):
    return await playlistdb.find_one({"user_id": user_id, "name": name})

async def get_all_playlists(user_id: int):
    return await playlistdb.find({"user_id": user_id}).to_list(length=None)

async def get_public_playlists(skip: int = 0, limit: int = 20):
    return await playlistdb.find({"is_public": True}).skip(skip).limit(limit).to_list(length=None)

async def rename_playlist(user_id: int, old_name: str, new_name: str) -> bool:
    result = await playlistdb.update_one(
        {"user_id": user_id, "name": old_name},
        {"$set": {"name": new_name}}
    )
    return result.modified_count > 0

async def set_playlist_visibility(user_id: int, name: str, is_public: bool) -> bool:
    result = await playlistdb.update_one(
        {"user_id": user_id, "name": name},
        {"$set": {"is_public": is_public}}
    )
    return result.modified_count > 0

async def add_track(user_id: int, name: str, track: dict) -> bool:
    result = await playlistdb.update_one(
        {"user_id": user_id, "name": name},
        {"$push": {"tracks": track}}
    )
    return result.modified_count > 0

async def remove_track(user_id: int, name: str, video_id: str) -> bool:
    # First get the playlist
    pl = await get_playlist(user_id, name)
    if not pl: return False
    # Find the track and remove it
    tracks = pl.get("tracks", [])
    new_tracks = [t for t in tracks if t.get("vidid") != video_id]
    if len(tracks) == len(new_tracks): return False
    
    result = await playlistdb.update_one(
        {"user_id": user_id, "name": name},
        {"$set": {"tracks": new_tracks}}
    )
    return result.modified_count > 0

async def clone_playlist(owner_id: int, original_name: str, new_user_id: int) -> bool:
    original = await get_playlist(owner_id, original_name)
    if not original:
        return False
        
    # Check if target user already has a playlist with this name
    if await get_playlist(new_user_id, original['name']):
        return False
        
    new_doc = {
        "user_id": new_user_id,
        "name": original['name'],
        "is_public": False,
        "tracks": original.get("tracks", [])
    }
    await playlistdb.insert_one(new_doc)
    return True
