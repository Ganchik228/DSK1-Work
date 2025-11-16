from fastapi import APIRouter
from .EoilPricerouter import eoilrout
from .GeneralPriceRouter import generalprout
from .StraightPriceRouter import straightprout
from .WagonPriceRouter import wagonprout


oilrouter = APIRouter(prefix="/oilPricesDynamic", tags=["OilPriceDynamic"])


oilrouter.include_router(eoilrout)
oilrouter.include_router(generalprout)
oilrouter.include_router(straightprout)
oilrouter.include_router(wagonprout)


@oilrouter.get("/")
async def root():
    return {"Message": "Nothing to see here"}
