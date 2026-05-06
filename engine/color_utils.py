from typing import TYPE_CHECKING
from cmu_graphics import rgb

if TYPE_CHECKING:
    from cmu_graphics.shape_logic import RGB
    
def set_brightness(color: "RGB", brightness: float) -> "RGB":
    assert isinstance(brightness, float) and 0 <= brightness <= 1
    return rgb(
        color.red * brightness,
        color.green * brightness,
        color.blue * brightness
    )