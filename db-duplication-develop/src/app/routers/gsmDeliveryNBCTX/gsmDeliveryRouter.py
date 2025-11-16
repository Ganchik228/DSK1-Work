from fastapi import APIRouter
from .maz045 import maz045rout
from .maz060 import maz060rout
from .maz315 import maz315rout
from .maz354 import maz354rout
from .maz370 import maz370rout
from .sitrak107 import sitrak107rout
from .sitrak142 import sitrak142rout
from .sitrak191 import sitrak191rout


gsmnbCTXrouter = APIRouter(prefix="/GsmnbCTX", tags=["GsmnbCTX"])

gsmnbCTXrouter.include_router(maz045rout)
gsmnbCTXrouter.include_router(maz060rout)
gsmnbCTXrouter.include_router(maz315rout)
gsmnbCTXrouter.include_router(maz354rout)
gsmnbCTXrouter.include_router(maz370rout)
gsmnbCTXrouter.include_router(sitrak107rout)
gsmnbCTXrouter.include_router(sitrak142rout)
gsmnbCTXrouter.include_router(sitrak191rout)


@gsmnbCTXrouter.get("/")
async def root():
    return {"Message": "Nothing to see here"}
