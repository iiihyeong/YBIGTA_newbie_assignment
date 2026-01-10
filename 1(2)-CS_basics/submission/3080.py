from dataclasses import dataclass, field
from typing import TypeVar, Generic, Optional, Iterable


"""
TODO:
- Trie.push 구현하기
- (필요할 경우) Trie에 추가 method 구현하기
"""


T = TypeVar("T")


@dataclass
class TrieNode(Generic[T]):
    body: Optional[T] = None
    children: list[int] = field(default_factory=lambda: [])
    is_end: bool = False


class Trie(list[TrieNode[T]]):
    def __init__(self) -> None:
        super().__init__()
        self.append(TrieNode(body=None))

    def push(self, seq: Iterable[T]) -> None:
        """
        seq: T의 열 (list[int]일 수도 있고 str일 수도 있고 등등...)

        action: trie에 seq을 저장하기

        각 seq의 element(혹은 자기 자신)이 trie에 있는지 확인하고, 없다면 맨 마지막 위치에
        새 노드를 저장하고 해당 위치로 이동합니다

        is_end: seq가 trie에 있지 않은 경우 True, 아니면 False입니다

        """
        current_idx = 0

        for char in seq:
            is_exist = False
            for child_idx in self[current_idx].children:
                if self[child_idx].body == char:
                    current_idx = child_idx
                    is_exist = True
                    break

            if not is_exist:
                new_node = TrieNode(body=char)
                self.append(new_node)
                new_idx = len(self) - 1
                self[current_idx].children.append(new_idx) 
                current_idx = new_idx

        self[current_idx].is_end = True        

    # 구현하세요!


import sys


"""
TODO:
- 일단 lib.py의 Trie Class부터 구현하기
- main 구현하기

힌트: 한 글자짜리 자료에도 그냥 str을 쓰기에는 메모리가 아깝다...
"""


def main() -> None:
    '''
    input: 풀이 검증에 걸리는 시간 단축용
    str 객체 대신 가벼운 int 리스트로 변환,
    단어들을 trie 구조로 쌓아
    반복문으로 모든 노드 방문

    branch_num: 현재 노드 아래에 있는 자식 노드들의 수
    이때 자식 노드 수가 0이면 계산을 위해 1로 설정됨

    모든 branch_num의 팩토리얼들을 곱한 값을 출력

    '''
    input = sys.stdin.readline
    N = int(input())
    
    trie: Trie[int] = Trie()

    for i in range(N):
        name = input().strip()
        ascii_seq = [ord(char) for char in name]
        trie.push(ascii_seq)
        
    ans = 1
    MOD = 1000000007

    for node in trie:
        branch_num = len(node.children)
        if node.is_end:
            branch_num += 1
        
        if branch_num > 1:
            for k in range(2, branch_num + 1):
                ans = (ans * k) % MOD
    print(ans)

if __name__ == "__main__":
    main()