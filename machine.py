from os import system
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

        self.cur_lines=len(self.drawn_lines)
        self.cur_triangles=len(self.triangles)

    def find_best_selection(self):
        (a, b)=self.max_move()
        return b
    
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
        ''' 게임 종료 확인 '''
        remain_to_draw = [[point1, point2] for (point1, point2) in list(combinations(self.whole_points, 2)) if self.check_availability([point1, point2])]
        return False if remain_to_draw else True

    def check_triangle(self, line):
        self.get_score = False

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
                    self.get_score = True
        return self.get_score

    def max_move(self):   # available = 연결가능한 모든 점 조합 리스트
        available = [[point1, point2] for (point1, point2) in list(combinations(self.whole_points, 2)) if self.check_availability([point1, point2])] 

        if self.check_endgame():
            turn=True # True = Machine, False=User
            for i in range(self.cur_lines+1,len(self.drawn_lines)+1):
                if self.check_triangle(self.drawn_lines[i]) and turn:
                    self.score[1]+=1
                    turn=False
                else:
                    turn=True
            return (self.score[1] , self.self.drawn_lines[self.cur_lines+1]) # 게임 종료 시 Machine score 값 리턴
        
        else:
            best_score=0
            best_move=[]
            for next_move in available:
                self.drawn_lines.append(next_move)
                node_score=self.min_move()

                if(node_score>best_score):
                    best_score=node_score
                    best_move=self.drawn_lines[-1]

                self.drawn_lines.pop()
            return (self.score[1] , best_move)
    

        
    def min_move(self):
        available = [[point1, point2] for (point1, point2) in list(combinations(self.whole_points, 2)) if self.check_availability([point1, point2])] 

        if self.check_endgame():
            turn=False # True = Machine, False=User
            for i in range(self.cur_lines+1,len(self.drawn_lines)+1):
                if self.check_triangle(self.drawn_lines[i]) and turn:
                    self.score[1]+=1
                    turn=True
                else:
                    turn=False
            return (self.score[1] , self.self.drawn_lines[self.cur_lines+1]) # 게임 종료 시 Machine score 값 리턴
        
        else:
            best_score=0
            best_move=[]
            for next_move in available:
                self.drawn_lines.append(next_move)
                node_score=self.max_move()

                if(node_score>best_score):
                    best_score=node_score
                    best_move=self.drawn_lines[-1]

                self.drawn_lines.pop()
            return (self.score[1] , best_move)


    
