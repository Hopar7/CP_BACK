from github import Github
import os
# GitHub 계정 정보

repo_name = 'img_test'

# 파일 경로와 파일 이름
file_name=''

# GitHub에 접속
g = Github(token)

# 레포지토리 가져오기
repo = g.get_user().get_repo(repo_name)



# 파일 업로드
async def git_push(file_path:str):
    print(file_path)
    with open(file_path, 'rb') as file:
        content = file.read()
        file_name = os.path.basename(file_path)
        repo.create_file(file_name, "바보가 되", content)