from lib import create_circular_queue


"""
TODO:
- simulate_card_game 구현하기
    # 카드 게임 시뮬레이션 구현
        # 1. 큐 생성
        # 2. 카드가 1장 남을 때까지 반복
        # 3. 마지막 남은 카드 반환
"""


def simulate_card_game(n: int) -> int:
    """
    카드2 문제의 시뮬레이션
    맨 위 카드를 버리고, 그 다음 카드를 맨 아래로 이동
    해당 과정을 queue의 길이가 1이 될 때까지 반복하면
    자동으로 마지막 요소값이 답안이 됩니다

    n(int) : 카드의 장수(=카드 번호의 최대값)

    """
    que = create_circular_queue(n)

    while len(que) > 1: 
        que.popleft()
        que.append(que.popleft())
    return que.popleft()


def solve_card2() -> None:
    """입, 출력 format"""
    n: int = int(input())
    result: int = simulate_card_game(n)
    print(result)

if __name__ == "__main__":
    solve_card2()