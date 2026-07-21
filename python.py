import requests
import time

# 1. Your Real-Debrid API Token (Get it from https://real-debrid.com/apitoken)
API_KEY = "YOUR_REAL_DEBRID_API_TOKEN"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# 2. Magnet link you want to convert
MAGNET_LINK = "magnet:?xt=urn:btih:EXAMPLE_TORRENT_HASH..."

def torrent_to_direct_link(magnet):
    # Step A: Add magnet link to Real-Debrid
    print("Adding magnet link...")
    add_url = "https://api.real-debrid.com/rest/1.0/torrents/addMagnet"
    response = requests.post(add_url, headers=HEADERS, data={"magnet": magnet}).json()
    torrent_id = response.get("id")
    
    if not torrent_id:
        print("Error adding magnet:", response)
        return

    # Step B: Select all files inside the torrent
    print(f"Torrent added (ID: {torrent_id}). Selecting files...")
    select_url = f"https://api.real-debrid.com/rest/1.0/torrents/selectFiles/{torrent_id}"
    requests.post(select_url, headers=HEADERS, data={"files": "all"})

    # Step C: Wait for cloud processing/caching
    print("Processing in the cloud...")
    info_url = f"https://api.real-debrid.com/rest/1.0/torrents/info/{torrent_id}"
    
    while True:
        info = requests.get(info_url, headers=HEADERS).json()
        status = info.get("status")
        
        if status == "downloaded":
            print("Download ready in cloud!")
            break
        elif status == "downloading":
            print(f"Downloading in cloud: {info.get('progress')}%...")
        time.sleep(2)

    # Step D: Unrestrict (un-debrid) the generated links into Direct Download URLs
    direct_links = []
    unrestrict_url = "https://api.real-debrid.com/rest/1.0/unrestrict/link"
    
    for link in info.get("links", []):
        unrestrict_resp = requests.post(unrestrict_url, headers=HEADERS, data={"link": link}).json()
        direct_download_url = unrestrict_resp.get("download")
        direct_links.append(direct_download_url)
        
    return direct_links

# Run the code
if __name__ == "__main__":
    links = torrent_to_direct_link(MAGNET_LINK)
    print("\n--- Direct Download Links (>29 MB/s Ready) ---")
    for dl in links:
        print(dl)