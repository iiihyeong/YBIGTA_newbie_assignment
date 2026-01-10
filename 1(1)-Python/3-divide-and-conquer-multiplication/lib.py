from __future__ import annotations
import copy


"""
TODO:
- __setitem__ 구현하기
- __pow__ 구현하기 (__matmul__을 활용해봅시다)
- __repr__ 구현하기
"""


class Matrix:
    MOD = 1000

    def __init__(self, matrix: list[list[int]]) -> None:
        self.matrix = matrix

    @staticmethod
    def full(n: int, shape: tuple[int, int]) -> Matrix:
        return Matrix([[n] * shape[1] for _ in range(shape[0])])

    @staticmethod
    def zeros(shape: tuple[int, int]) -> Matrix:
        return Matrix.full(0, shape)

    @staticmethod
    def ones(shape: tuple[int, int]) -> Matrix:
        return Matrix.full(1, shape)

    @staticmethod
    def eye(n: int) -> Matrix:
        matrix = Matrix.zeros((n, n))
        for i in range(n):
            matrix[i, i] = 1
        return matrix

    @property
    def shape(self) -> tuple[int, int]:
        return (len(self.matrix), len(self.matrix[0]))

    def clone(self) -> Matrix:
        return Matrix(copy.deepcopy(self.matrix))

    def __getitem__(self, key: tuple[int, int]) -> int:
        return self.matrix[key[0]][key[1]]

    def __setitem__(self, key: tuple[int, int], value: int) -> None:
        '''
        key는 (행, 열)로 구성된 튜플입니다.
        해당 위치의 element를 파라미터로 받은 value값으로 설정합니다
        이후 해당 위치에 MOD 연산을 수행하여 저장됩니다
        '''
        self.matrix[key[0]][key[1]] = value % self.MOD

    def __matmul__(self, matrix: Matrix) -> Matrix:
        x, m = self.shape
        m1, y = matrix.shape
        assert m == m1

        result = self.zeros((x, y))

        for i in range(x):
            for j in range(y):
                for k in range(m):
                    result[i, j] += self[i, k] * matrix[k, j]

        return result

    def __pow__(self, n: int) -> Matrix:
        '''
        1629 문제처럼, 제곱을 여러번 재귀 수행하고 나머지 수행해야 할 곱셉은 홀수 여부에 따라 실행됩니다
        이떄 행렬 곱이므로 '*' 대신 '@'를 사용합니다
        '''
        if n == 1:
            return Matrix.eye(self.shape[0]) @ self
        temp = self.__pow__(n // 2)
        answer = temp @ temp
        if n % 2 == 1:
            answer = answer @ self
        
        return answer
        

    def __repr__(self) -> str:
        '''
        행렬 출력 형태를 지정하는 메소드입니다
        문제 포맷에 따라, 각 행별 줄바꿈와 열별 띄어쓰기를 구현하여
        매트릭스의 각 요소들을 str로 차례대로 출력합니다
        '''
        line_list = []
        for row in self.matrix:
            line = " ".join(map(str, row))
            line_list.append(line)

        return "\n".join(line_list)