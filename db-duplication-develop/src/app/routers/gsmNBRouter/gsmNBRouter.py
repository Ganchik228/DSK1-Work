from fastapi import APIRouter
from .maz045 import maz045rout
from .maz060 import maz060rout
from .maz315 import maz315rout
from .maz354 import maz354rout
from .maz370 import maz370rout
from .sitrak107 import sitrak107rout
from .sitrak142 import sitrak142rout
from .sitrak191 import sitrak191rout


gsmNBrouter = APIRouter(prefix="/GsmNB", tags=["GsmNB"])


gsmNBrouter.include_router(maz045rout)
gsmNBrouter.include_router(maz060rout)
gsmNBrouter.include_router(maz315rout)
gsmNBrouter.include_router(maz354rout)
gsmNBrouter.include_router(maz370rout)
gsmNBrouter.include_router(sitrak107rout)
gsmNBrouter.include_router(sitrak142rout)
gsmNBrouter.include_router(sitrak191rout)


@gsmNBrouter.get("/")
async def root():
    return {"Message": "Nothing to see here"}
