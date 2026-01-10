from __future__ import annotations
import copy
from collections import deque
from collections import defaultdict
from typing import DefaultDict, List


"""
TODO:
- __init__ 구현하기
- add_edge 구현하기
- dfs 구현하기 (재귀 또는 스택 방식 선택)
- bfs 구현하기
"""


class Graph:
    def __init__(self, n: int) -> None:
        """
        그래프 초기화
        n: 정점의 개수 (1번부터 n번까지)
        """
        self.n = n

        self.graph: dict[int, list[int]] = {}
        for i in range(n+1):
            self.graph[i] = []
        

    
    def add_edge(self, u: int, v: int) -> None:
        """
        양방향 간선 추가
        """
        self.graph[u].append(v)
        self.graph[v].append(u)
        
        
    
    
    def dfs(self, start: int) -> list[int]:
        """
        깊이 우선 탐색(DFS)를 재귀적으로 실행하여 방문한 정점 순서 리스트를 반환합니다.

        각 노드에 연결된 노드들을 정렬하여,
        
        방문할 수 있는 정점이 여러 개인 경우 정점 번호가 작은 것을 먼저 방문합니다.
        
        Args:
            start (int): 탐색을 시작하는 정점.
            
        Returns:
            list[int]: 탐색하며 방문한 정점들이 순서대로 담긴 리스트.
        """
        for key in self.graph:
            self.graph[key].sort()

        answer = []

        def _recursive_dfs(node: int):

            answer.append(node)
            for nei in self.graph[node]:
                if nei not in answer:
                    _recursive_dfs(nei)

            return answer
        
        _recursive_dfs(start)
        return answer

    def bfs(self, start: int) -> list[int]:
        """
        너비 우선 탐색 (BFS)를 재귀적으로 실행하여 방문한 정점 순서 리스트를 반환합니다.

        먼저 DFS와 같이 각 노드에 연결된 노드들을 정렬합니다

        큐를 사용하여, 큐에서 반환된 노드가 큐 맨 뒤에 자신과 연결된 하위 노드들을 담도록 합니다

        Args:
            start (int): 탐색을 시작하는 정점.
            
        Returns:
            list[int]: 탐색하며 방문한 정점들이 순서대로 담긴 리스트.
        """

        for key in self.graph:
            self.graph[key].sort()
            
        que = deque([start])

        answer = [start]

        while que:
            v = que.popleft()
            
            for nei in self.graph[v]:
                if nei not in answer:
                    answer.append(nei) 
                    que.append(nei)  
                    
        return answer
    
    def search_and_print(self, start: int) -> None:
        """
        DFS와 BFS 결과를 출력
        """
        dfs_result = self.dfs(start)
        bfs_result = self.bfs(start)
        
        print(' '.join(map(str, dfs_result)))
        print(' '.join(map(str, bfs_result)))



from typing import Callable
import sys


"""
-아무것도 수정하지 마세요!
"""


def main() -> None:
    intify: Callable[[str], list[int]] = lambda l: [*map(int, l.split())]

    lines: list[str] = sys.stdin.readlines()

    N, M, V = intify(lines[0])
    
    graph = Graph(N)  # 그래프 생성
    
    for i in range(1, M + 1): # 간선 정보 입력
        u, v = intify(lines[i])
        graph.add_edge(u, v)
    
    graph.search_and_print(V) # DFS와 BFS 수행 및 출력


if __name__ == "__main__":
    main()
