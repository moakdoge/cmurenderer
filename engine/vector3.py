import math


class Vector3():
    __slots__ = ("x", "y", "z")
    def __init__(self, x, y, z) -> None:
        self.x=x
        self.y=y
        self.z=z
    @classmethod
    def new(cls, x,y,z):
        return cls(x=x,y=y,z=z)
    @classmethod
    def zero(cls) -> "Vector3":
        return cls(x=0,y=0,z=0)
    @property
    def normal(self):
        mag = math.sqrt((self.x*self.x)+ (self.y*self.y) + (self.z*self.z))
        if mag == 0:
            return Vector3(0,0,0)
        return Vector3.new(self.x/mag, self.y/mag, self.z/mag)
    @property
    def offscreen(self) -> bool:
        BUFFER=150
        if self.screen is None:
            return True
        x,y=self.screen if self.screen is not None else (-999999999999, -1)
        return (x < -BUFFER or x > 400+BUFFER) or (y < -BUFFER or y > 400+BUFFER)
    @property
    def screen(self, width=400, height=400) -> tuple[int, int]:
        focal = 150
        camera_offset = 0
        z = self.z + camera_offset
        if z <= 0:
            return (-1, -1)
        aspect = height / width
        screen_x = (self.x / z) * focal + width / 2
        screen_y = -(self.y / z) * focal * aspect + height / 2  # flip Y
        return screen_x, screen_y

    #operators
    def __mul__(self, other):
        # v * number
        if isinstance(other, (int, float)):
            return Vector3(
                self.x * other,
                self.y * other,
                self.z * other
            )
        raise TypeError("Can only multiply Vector3 by scalar")
    def __add__(self, other: "Vector3") -> "Vector3":
        if isinstance(other, Vector3):
            return Vector3(
                self.x + other.x,
                self.y + other.y,
                self.z + other.z
            )
    def __sub__(self, other: "Vector3") -> "Vector3":
        if isinstance(other, Vector3):
            return Vector3(
                self.x - other.x,
                self.y - other.y,
                self.z - other.z
            )
        
    def __repr__(self) -> str:
        return f"({math.ceil(self.x)}, {math.ceil(self.y)}, {math.ceil(self.z)})"
    def __str__(self) -> str:
        return self.__repr__()
    def __neg__(self):
        return Vector3(-self.x, -self.y, -self.z)
    

    #math functions
    def _qscos(self, angle):
        s = math.sin(angle)
        c = math.cos(angle)
        return s, c

    def rotate_x(self, angle):
        sin_theta, cos_theta = self._qscos(angle)
        y = self.y * cos_theta - self.z * sin_theta
        z = self.y * sin_theta + self.z * cos_theta
        return Vector3(self.x, y, z)

    def rotate_y(self, angle):
        sin_theta, cos_theta = self._qscos(angle)
        x = self.x * cos_theta + self.z * sin_theta
        z = -self.x * sin_theta + self.z * cos_theta
        return Vector3(x, self.y, z)

    def rotate_z(self, angle):
        sin_theta, cos_theta = self._qscos(angle)
        x = self.x * cos_theta - self.y * sin_theta
        y = self.x * sin_theta + self.y * cos_theta
        return Vector3(x, y, self.z)

    def rotate(self, angle: "Vector3"):
        m = self.rotate_y(angle.y)
        m = m.rotate_x(angle.x)
        m = m.rotate_z(angle.z)
        return m
    def rotate_xyz(self, angle):
        sin_theta, cos_theta = self._qscos(angle)

        #rotate x
        y = self.y * cos_theta - self.z * sin_theta
        z = self.y * sin_theta + self.z * cos_theta

        #rotate y
        x = self.x * cos_theta + z * sin_theta
        z = -self.x * sin_theta + z * cos_theta

        #rotate z
        x = x * cos_theta - y * sin_theta
        y = x * sin_theta + y * cos_theta

        return Vector3.new(x,y,z)
    
    def cross(self, other):
        return Vector3(
            self.y * other.z - self.z * other.y,  # i
            self.z * other.x - self.x * other.z,  # j
            self.x * other.y - self.y * other.x   # k
        )
    
    def distance(self, other):
        return math.sqrt((other.x-self.x)**2+(other.y-self.y)**2+(other.z-self.z)**2)
    
    def dot(self, b):
        return self.x * b.x + self.y * b.y + self.z * b.z

