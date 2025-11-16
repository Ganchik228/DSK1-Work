from fastapi import APIRouter
from .maz045 import maz045rout
from .maz060 import maz060rout
from .maz315 import maz315rout
from .sitrak107 import sitrak107rout
from .sitrak142 import sitrak142rout
from .sitrak191 import sitrak191rout


gsmMegionrouter = APIRouter(prefix="/GsmMegion", tags=["GsmMegion"])

gsmMegionrouter.include_router(maz045rout)
gsmMegionrouter.include_router(maz060rout)
gsmMegionrouter.include_router(maz315rout)
gsmMegionrouter.include_router(sitrak107rout)
gsmMegionrouter.include_router(sitrak142rout)
gsmMegionrouter.include_router(sitrak191rout)


@gsmMegionrouter.get("/")
async def root():
    return {"Message": "Nothing to see here"}
