from lib import create_circular_queue, rotate_and_remove


"""
TODO:
- josephus_problem 구현하기
    # 요세푸스 문제 구현
        # 1. 큐 생성
        # 2. 큐가 빌 때까지 반복
        # 3. 제거 순서 리스트 반환
"""


def josephus_problem(n: int, k: int) -> list[int]:
    """
    요세푸스 문제 해결
    n명 중 k번째마다 제거하는 순서를 반환

    n개의 번호가 담긴 queue가 없어질 때까지 k번째 요소를 뽑아 리스트에 담는 걸 반복
    이때, deque 성질로 맨 뒤 element의 다음 순서로 맨 처음 element로 돌아가기에 성립
    """
    queue = create_circular_queue(n)

    answer = []

    while queue:
        removed_person = rotate_and_remove(queue, k)
        answer.append(removed_person)
        
    return answer

def solve_josephus() -> None:
    """입, 출력 format"""
    n: int
    k: int
    n, k = map(int, input().split())
    result: list[int] = josephus_problem(n, k)
    
    # 출력 형식: <3, 6, 2, 7, 5, 1, 4>
    print("<" + ", ".join(map(str, result)) + ">")

if __name__ == "__main__":
    solve_josephus()