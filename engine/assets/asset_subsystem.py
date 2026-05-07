from typing import TYPE_CHECKING



from engine.assets.asset import Asset
from engine.assets.asset_type import AssetType
from engine.extras import dataclass
from cmu_graphics import Image
if TYPE_CHECKING:
    from engine._game import Game
    
@dataclass()
class AssetSubsystem():
    parent: "Game"
    def load_asset(self, asset: Asset) -> str:
        '''Gets the URL for the respective asset'''
        assert isinstance(asset, Asset)
        
        #okay, we have an image.
        if self.parent.utils.is_web():
            return asset.cmu_path
        return asset.desktop_path
    
    def verify_asset(self, asset: Asset) -> bool:
        try:
            with open(f"{self.parent.utils.backend_url}{self.load_asset(asset)}", "rb") as f:
                pass
        except FileNotFoundError as e:
            return False
        return True


        