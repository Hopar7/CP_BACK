from thefuzz import fuzz
from domains.users.service import ContentService
from domains.users.repositories import ContentRepository


def searchtext(searchtext,contents_list): #user_controller에서 배열과 스트링 받아옴 
    similarities = []
    title_searched_indices = set()
    for i in range(len(contents_list)):
        title_similarity = fuzz.partial_ratio(contents_list[i].title, searchtext)
        if title_similarity >= 51:
            similarities.append((i, contents_list[i], title_similarity))
            title_searched_indices.add(i)  # 검색된 인덱스를 집합에 추가

    # Text에서 검색 (title에서 검색된 인덱스를 제외)
    for i in range(len(contents_list)):
        if i not in title_searched_indices:  # title에서 검색되지 않은 인덱스만
            text_similarity = fuzz.partial_ratio(contents_list[i].text, searchtext)
            if text_similarity >= 51:
                similarities.append((i, contents_list[i], text_similarity))
            #contents_list를 받아와서 이걸 추가해야하는데

    # 유사도에 따라 내림차순으로 정렬
    similarities.sort(key=lambda x: x[2], reverse=True)

    # 정렬된 리스트 출력
    for idx, contents_list, similarity in similarities:
        print(f"Index: {idx}, Content: {contents_list}, Similarity: {similarity}")
    
    result = [item[1] for item in similarities]
    return result

    #정렬한 유사도 높은순의 데이터를 DTO에 대입하여 정보를 클라이언트에 전달
    #유사도 50보다 낮으면 없음 처리



   

    

    