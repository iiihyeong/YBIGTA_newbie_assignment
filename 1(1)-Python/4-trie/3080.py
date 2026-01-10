from lib import Trie
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
    
    trie = Trie()

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