from cmath import inf
from itertools import combinations,chain,product
from shapely.geometry import LineString, Point,Polygon


class MACHINE():
    """
        [ MACHINE ]
        MinMax Algorithm을 통해 수를 선택하는 객체.
        - 모든 Machine Turn마다 변수들이 업데이트 됨

        ** To Do **
        MinMax Algorithm을 이용하여 최적의 수를 찾는 알고리즘 생성
           - class 내에 함수를 추가할 수 있음
           - 최종 결과는 find_best_selection을 통해 Line 형태로 도출
               * Line: [(x1, y1), (x2, y2)] -> MACHINE class에서는 x값이 작은 점이 항상 왼쪽에 위치할 필요는 없음 (System이 organize 함)
    """
    def __init__(self, score=[0, 0], drawn_lines=[], whole_lines=[], whole_points=[], location=[]):
        self.id = "MACHINE"
        self.score = [0, 0] # USER, MACHINE
        self.drawn_lines = [] # Drawn Lines
        self.board_size = 7 # 7 x 7 Matrix
        self.num_dots = 0
        self.whole_points = []
        self.location = []
        self.triangles = [] # [(a, b), (c, d), (e, f)]
        self.best_move= []

    def find_best_selection(self):
        # First, try using the heuristic algorithm
        best_selection = self.heuristic_algorithm(self.get_available_lines())

        # If no independent lines are available, switch to minmax_move
        if not best_selection:
            print("민맥스")
            best_selection = self.minmax_move(-100, 100, 2)[1]

        print("휴리스틱")
        return best_selection

    def get_available_lines(self):
        return [[point1, point2] for (point1, point2) in
                list(combinations(self.whole_points, 2)) if self.check_availability([point1, point2])]

    def heuristic_algorithm(self, available):
        is_first_player = len(self.drawn_lines) % 2

        if not available:
            return None

        if is_first_player == 0:
            print("선공입니다.")
        else:
            print("후공입니다.")

        # 선분 연결 가중치
        connected_weights = {point: 0 for point in self.whole_points}
        for line in self.drawn_lines:
            for point in line:
                connected_weights[point] += 1

        # 휴리스틱 값 계산
        heuristic_values = []
        for line in available:
            value = 0
            for point in line:
                value += connected_weights[point]

            # 후공 특이사항: 이미 그어진 선분에 이어져서 직선을 이룰 수 있는 선분 선호
            if not is_first_player:
                for drawn_line in self.drawn_lines:
                    if line[0] in drawn_line or line[1] in drawn_line:
                        value += 3  # 가중치를 크게 더함

            # 독립된 선분 가중치 추가
            independent_line_weight = 2  # 독립된 선분 가중치
            drawn_points = [point for drawn_line in self.drawn_lines for point in drawn_line]
            if line[0] not in drawn_points and line[1] not in drawn_points:
                value += independent_line_weight

            # 즉시 삼각형 생성 가능 여부 확인
            t=self.check_triangle(line)
            if  t > 0:
                for i in range(t):
                    self.triangles.pop()
                value += 5  # 큰 가중치 부여
            heuristic_values.append((line, value))

        # 선분들의 휴리스틱 가중치 출력
        for line, value in heuristic_values:
            print(f"선분 {line}의 휴리스틱 가중치: {value}")

        # 휴리스틱 값에 따라 정렬
        heuristic_values.sort(key=lambda x: x[1], reverse=True)

        # 최상의 선분 반환
        return heuristic_values[0][0]



    def check_availability(self, line):
        line_string = LineString(line)


        # Must be one of the whole points
        condition1 = (line[0] in self.whole_points) and (line[1] in self.whole_points)
        
        # Must not skip a dot
        condition2 = True
        for point in self.whole_points:
            if point==line[0] or point==line[1]:
                continue
            else:
                if bool(line_string.intersection(Point(point))):
                    condition2 = False

        # Must not cross another line
        condition3 = True
        for l in self.drawn_lines:
            if len(list(set([line[0], line[1], l[0], l[1]]))) == 3:
                continue
            elif bool(line_string.intersection(LineString(l))):
                condition3 = False

        # Must be a new lineturn
        condition4 = (line not in self.drawn_lines)

        if condition1 and condition2 and condition3 and condition4:
            return True
        else:
            return False
    
    def check_endgame(self):
        remain_to_draw = [[point1, point2] for (point1, point2) in list(combinations(self.whole_points, 2)) if self.check_availability([point1, point2])]
        return False if remain_to_draw else True
     

        
    def minmax_move(self, alpha, beta, depth):
        turn = len(self.drawn_lines) % 2  # 0: my, 1: OPPONENT

        if self.check_endgame() or depth == 0: 
            return self.score[1]-self.score[0], None # return score, best_move
         # available = 연결가능한 모든 점 조합 리스트
        available = [[point1, point2] for (point1, point2) in list(combinations(self.whole_points, 2)) if self.check_availability([point1, point2])]

        best_move = None # best_move = (x1, y1), (x2, y2)

        if turn == 0:  # my turn
            max_val = -inf
            for next_move in available:
                get_score = self.check_triangle(next_move)
                if get_score > 0:
                    self.score[1] += get_score
                self.drawn_lines.append(next_move)

                result, _ = self.minmax_move(alpha, beta, depth - 1) 

                if get_score > 0:  # 삼각형이 추가되었다면 pop
                    for i in range (get_score):
                        self.triangles.pop()
                    self.score[1] -= get_score
                self.drawn_lines.pop()

                if result > max_val: # return 값 갱신
                    max_val = result
                    best_move = next_move

                alpha = max(alpha, max_val) # alpha 값 갱신
                if beta <= alpha:
                    break

            return max_val, best_move

        else:  # opponent's turn (minimize) 동일
            min_val = inf
            for next_move in available:
                get_score = self.check_triangle(next_move)
                if get_score > 0:
                    self.score[0] += get_score
                self.drawn_lines.append(next_move)

                result, _ = self.minmax_move(alpha, beta, depth - 1)

                if get_score > 0:  # 삼각형이 추가되었다면 pop
                    for i in range (get_score):
                        self.triangles.pop()
                    self.score[0] -= get_score
                self.drawn_lines.pop()

                if result < min_val:
                    min_val = result
                    best_move = next_move

                beta = min(beta, min_val)
                if beta <= alpha:
                    break

            return min_val, best_move


    def check_triangle(self, line):
        tri_count=0
        point1 = line[0]
        point2 = line[1]

        point1_connected = []
        point2_connected = []

        for l in self.drawn_lines:
            if l == line:  # 자기 자신 제외
                continue
            if point1 in l:
                point1_connected.append(l)
            if point2 in l:
                point2_connected.append(l)

        if point1_connected and point2_connected: # 최소한 2점 모두 다른 선분과 연결되어 있어야 함
            for line1, line2 in product(point1_connected, point2_connected):
                
                # Check if it is a triangle & Skip the triangle has occupied
                triangle = self.organize_points(list(set(chain(*[line, line1, line2]))))
                if len(triangle) != 3 or triangle in self.triangles:
                    continue

                empty = True
                for point in self.whole_points:
                    if point in triangle:
                        continue
                    if bool(Polygon(triangle).intersection(Point(point))):
                        empty = False

               
                if empty:
                    self.triangles.append(triangle)
                    tri_count+=1
                
        return tri_count


    def organize_points(self, point_list):
        point_list.sort(key=lambda x: (x[0], x[1]))
        return point_list
