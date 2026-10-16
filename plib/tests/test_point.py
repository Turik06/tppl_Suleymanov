import pytest
from plib import Point


@pytest.fixture
def points():
    p1 = Point(0,0)
    p2 = Point(1,1)
    p3 = Point(2,3)
    return p1 ,p2,p3
    
class TestPoint:

    def test_creation(self):
        try:
            Point(1,2)
        except Exception as e:
            pytest.fail(f"Failed with exception '{type(e)}'")


    def test_addition(self,points):
        p1,p2,p3 = points
        assert p1+p2 == Point(1,1)
        assert p1+p3 == Point(2,3)
        assert p2+p3 == Point(3,4)


    def test_eq(self,points):
        p1,p2,_= points
        assert p1 != p2
        with pytest.raises(NotImplementedError):
            assert p1 == [0,0]


    def test_subtraction(self,points):
        p1,p2,p3 = points
        assert p1-p2 == Point(-1,-1)
        assert p1-p3 == Point(-2,-3)
        assert p2-p3 == Point(-1,-2)


    @pytest.mark.parametrize(
            "p1,p2,distance",
            [(Point(0,0),Point(0,0),0),
             (Point(1,0),Point(0,0),1),
             (Point(0,1),Point(0,0),1),
             (Point(1,1),Point(0,0),1.4)]
    )
    def test_distance_to(self,p1,p2,distance):
        
        assert p1.distance_to(p2) == pytest.approx(distance,0.1)


    def test_str(self):
        assert str(Point(0,0)) == "Point(0,0)"


    def test_to_json(self):
        assert Point(0,0).to_json() == '{"x": 0, "y": 0}'


    def test_from_json(self):
        s = '{"x":0,"y":0}'
        assert Point.from_json(s) == Point(0,0)