import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def upload_short(video_path: str, title: str, description: str, tags: list[str]):
    print("🚀 Authenticating with YouTube...")
    credentials = None
    token_path = "token.json"
    
    if os.path.exists(token_path):
        credentials = Credentials.from_authorized_user_file(token_path, SCOPES)
        
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                "client_secret.json", SCOPES
            )
            credentials = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(credentials.to_json())

    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

    print(f"📤 Uploading {video_path} to YouTube Shorts...")
    
    # Ensure #Shorts is in the description/title so YouTube categorizes it properly
    full_description = f"{description}\n\n#Shorts #TechTrivia #SoftwareEngineering"

    body = {
        "snippet": {
            "title": f"{title} #Shorts",
            "description": full_description,
            "tags": tags + ["Shorts", "Tech", "Programming"],
            "categoryId": "28" # Science & Technology
        },
        "status": {
            "privacyStatus": "public", # Change to "private" or "unlisted" if testing
            "selfDeclaredMadeForKids": False
        }
    }

    from googleapiclient.http import MediaFileUpload
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"📦 Upload progress: {int(status.progress() * 100)}%")

    print(f"✨ Successfully uploaded! Video ID: {response.get('id')}")
    print(f"🔗 Watch here: https://youtu.be/{response.get('id')}")

if __name__ == "__main__":
    upload_short(
        video_path="remotion_src/out/tech-quiz.mp4",
        title="Can you solve this coding trivia?",
        description="Test your software engineering knowledge with this quick daily quiz!",
        tags=["Coding", "Python", "React", "SoftwareEngineer"]
    )
