import random
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
        self.tricheck = TRICHECK()

    def find_best_selection(self):
        ''''''
    
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

        # Must be a new line
        condition4 = (line not in self.drawn_lines)

        if condition1 and condition2 and condition3 and condition4:
            return True
        else:
            return False
    
    def check_endgame(self):
        ''' 게임 종료 확인 '''

    def max_move(self,line_apnd_list):   # available = 연결가능한 모든 점 조합 리스트
        available = [[point1, point2] for (point1, point2) in list(combinations(self.whole_points, 2)) if self.check_availability([point1, point2])] 

        if self.check_endgame(): # 종료 판단이 되었을 때 추가된 라인에 대해 점수 계산
            self.tricheck.score = self.score
            self.tricheck.drawn_lines = self.drawn_lines
            self.tricheck.whole_points = self.whole_points
            self.tricheck.location = self.location
            self.tricheck.triangles = self.triangles

            return (self.tricheck.check_triangle(line_apnd_list),line_apnd_list)
                
        
        else:  # 종료가 아닐때
            best_score=0
            best_move=[]

            for next_move in available:   # 모든 가능한 라인에 대해
                line_apnd_list.append(next_move)
                node_score=self.min_move(line_apnd_list)  # min_move 호출

                if(node_score>best_score):
                    best_score=node_score
                    best_move=line_apnd_list

                line_apnd_list.pop()

            return (best_score,best_move)
        
    
class TRICHECK():
    def __init__(self, score=[0, 0], drawn_lines=[], whole_lines=[], whole_points=[], location=[]):
        self.id = "TRICHECK"
        self.score = [0, 0] # USER, MACHINE
        self.drawn_lines = [] # Drawn Lines
        self.board_size = 7 # 7 x 7 Matrix
        self.num_dots = 0
        self.whole_points = []
        self.location = []
        self.triangles = [] # [(a, b), (c, d), (e, f)]

    def check_triangle(self, line_apended):

        turn=1 #user=0 machine=1
        for line in line_apended:
            point1 = line[0]
            point2 = line[1]

            point1_connected = []
            point2_connected = []

            for l in self.drawn_lines:
                if l==line: # 자기 자신 제외
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
                        self.score[turn]+=1

            if turn: turn=0  #turn change
            else: turn=1

        return self.score[1] #machine score return

    def organize_points(self, point_list):
        point_list.sort(key=lambda x: (x[0], x[1]))
        return point_list
