# lib.py의 Matrix 클래스를 참조하지 않음
import sys


"""
TODO:
- fast_power 구현하기 
"""


def fast_power(base: int, exp: int, mod: int) -> int:
    """
    빠른 거듭제곱 알고리즘 구현
    분할 정복을 이용, 시간복잡도 고민!

    int번 제곱하는 건, 제곱을 가능한 만큼 여러 번 한 다음 남은 수만큼 자기 자신을 곱해주면 해결
    즉 제곱하는 로직을 재귀적으로 처리

    또한 mod로 나누는 것도 공간 복잡도 측면에서 제곱 로직과 같이 재귀적으로 처리
    모듈러 연산 이용: (a * b) % c = ((a % c) * (b % c)) % c
    """
    if exp == 1:
        return base % mod
    
    temp = fast_power(base, exp // 2, mod)

    answer = (temp * temp) % mod

    if exp % 2 == 1:
        answer = (answer * base) % mod

    return answer

def main() -> None:
    A: int
    B: int
    C: int
    A, B, C = map(int, input().split()) # 입력 고정
    
    result: int = fast_power(A, B, C) # 출력 형식
    print(result) 

if __name__ == "__main__":
    main()
