from cmu_graphics import Polygon

class PolygonFactory:
    def __init__(self, size: int = 2000) -> None:
        self._pool: list[Polygon] = [
            Polygon(0, 0, 0, 0, 0, 0, visible=False)
            for _ in range(size)
        ]

        self._free: list[Polygon] = self._pool.copy()
        self._in_use: set[Polygon] = set()

    def reserve(self) -> Polygon:
        if not self._free:
            raise RuntimeError("Polygon pool exhausted")

        poly = self._free.pop()
        self._in_use.add(poly)

        poly.visible = True
        return poly

    def free(self, poly: Polygon) -> None:
        if poly not in self._in_use:
            raise RuntimeError("Tried to free polygon that is not currently reserved")

        self._in_use.remove(poly)
        self._free.append(poly)

        poly.visible = False