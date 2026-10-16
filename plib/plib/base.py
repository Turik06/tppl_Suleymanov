import math
import json

class Point:

    def __init__(self,x:int,y:int):
        if not isinstance(x,int) or not isinstance(y,int):
            raise TypeError("x,y should be an integer type")
        self.x = x
        self.y = y


    def __add__(self, other:Point) -> Point:
        return Point(self.x + other.x,
                     self.y + other.y)


    def __sub__(self,other:Point) -> Point:
        return Point(self.x - other.x,self.y - other.y)

    def __rsub__(self, other):
        pass

    def __eq__(self, other:object) -> bool:
        if not isinstance(other,Point):
            raise NotImplementedError
        return self.x == other.x and self.y == other.y


    def distance_to(self,other:Point) ->float:
        return math.sqrt((other.x - self.x)**2 + (other.y - self.y)**2)

    def __str__(self):
        return f"Point({self.x},{self.y})"

    def to_json(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(js):
        s = json.loads(js)
        return Point(s["x"], s["y"])