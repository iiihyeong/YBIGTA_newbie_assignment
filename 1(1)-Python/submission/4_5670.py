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
- 일단 Trie부터 구현하기
- count 구현하기
- main 구현하기
"""


def count(trie: Trie, query_seq: str) -> int:
    """
    trie - 이름 그대로 trie
    query_seq - 단어 ("hello", "goodbye", "structures" 등)

    returns: query_seq의 단어를 입력하기 위해 버튼을 눌러야 하는 횟수
    """
    pointer = 0
    cnt = 0

    for element in query_seq:
        if len(trie[pointer].children) > 1 or trie[pointer].is_end:
            cnt += 1

        new_index = None # 구현하세요!

        pointer = new_index

    return cnt + int(len(trie[0].children) == 1)


def main() -> None:
    # 구현하세요!
    pass


if __name__ == "__main__":
    main()