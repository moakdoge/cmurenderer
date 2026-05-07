from engine.extras import dataclass
from engine.assets.asset_type import AssetType

@dataclass(frozen=True, slots=True)
class Asset:
    desktop_path: str
    cmu_path: str
    asset_type: AssetType = AssetType.IMAGE