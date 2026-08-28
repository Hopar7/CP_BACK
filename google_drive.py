import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 구글 드라이브 API 사용을 위한 서비스 계정 키 경로
SERVICE_ACCOUNT_FILE = './bebid_tuter.json'

# 구글 드라이브 API 버전 및 서비스 객체 생성
SCOPES = ['https://www.googleapis.com/auth/drive']
service = build('drive', 'v3', credentials=service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES))

# 업로드할 파일의 경로와 파일 이름 지정
file_path = 'C:\\Users\\junsoo\\Desktop\\test\\dw.jpg'  # 이미지 파일의 경로
file_name = 'dw.jpg'  # 이미지 파일의 이름

parent_folder_id = '1-1w_h8t3ICtJRC57iUuTG-Mwy5sUFXJQ'

def upload_file_to_drive(file_path, file_name):
    # 업로드할 파일의 메타데이터 설정
    file_metadata = {
        'name': file_name,
        'parents': [parent_folder_id]
    }

    try:
        # 파일 업로드 설정
        media = MediaFileUpload(file_path, mimetype='image/jpeg')

        # 파일 업로드
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get('id')
        print(f'File {file_name} uploaded with ID: {file_id}')

        # 파일에 대한 링크 생성
        file_url = f'https://drive.google.com/file/d/{file_id}/view?usp=sharing'
        print(f'File URL: {file_url}')

        # 파일 호스트 계정 보여주기
        file_info = service.files().get(fileId=file_id, fields='owners').execute()
        owners = file_info.get('owners', [])
        if owners:
            owner_email = owners[0]['emailAddress']
            print(f'Host account: {owner_email}')
        else:
            print('No host account found.')

        # 파일을 공개로 설정
        permission = {
            'type': 'anyone',
            'role': 'reader'
        }
        service.permissions().create(fileId=file_id, body=permission).execute()
        print(f'File {file_id} is now public.')

    except Exception as e:
        print(f'An error occurred: {e}')
