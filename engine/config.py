from engine.extras import dataclass
from engine.cmu_utils import CMUtils



@dataclass(slots=True)
class DebugConfiguration:
    debug: bool = True
    wireframe: bool = False
    
@dataclass(slots=True)
class PerformanceConfiguration:
    minimum_physical_area_cull: int = 50_000
    zbuffer_enabled: bool = True
    zbuffer_size: int = 6
    max_triangles: int = 1950
    shading: bool = True
    quality: float = 0.8
    shadows: bool = False
    collisions: bool = True





@dataclass(slots=True)
class GameConfiguration:
    debug: DebugConfiguration = DebugConfiguration()
    web: PerformanceConfiguration = PerformanceConfiguration(
        zbuffer_size=8,
        max_triangles=400,
        shading=False,
        quality=0.25,
        shadows=False,
        collisions=False
    )
    desktop: PerformanceConfiguration = PerformanceConfiguration()
    
    #used to just get whatever the current one is
    @property
    def current(self) -> PerformanceConfiguration:
        if CMUtils.is_desktop():
            return self.desktop
        return self.web
    
    '''
    min_physical_area_cull: int = 50_000
    backface_cull: bool = False
    zbuffer: bool = True
    zbuffer_scale: int = 6 if utils.is_desktop() else 18
    fog: float = 1.25 #the strength of the fog
    max_triangles: int = 1950
    shading: bool = True
    quality: float = 0.8  #increase for worse quality
    cmu_quality: float = 0.125 #for CMU WEB only
    fps_target: int = 30
    min_quality: float = 0.25 if utils.is_desktop() else 0.01
    shadows: bool = utils.is_desktop()
    '''