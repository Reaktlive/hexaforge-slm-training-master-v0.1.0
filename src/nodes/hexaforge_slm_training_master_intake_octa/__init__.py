from fastapi import APIRouter
from .port_xi import router as _r_xi
from .port_xo import router as _r_xo
from .port_yi import router as _r_yi
from .port_yo import router as _r_yo
from .port_zi import router as _r_zi
from .port_zo import router as _r_zo
from .port_mi import router as _r_mi
from .port_mo import router as _r_mo

router = APIRouter()
router.include_router(_r_xi)
router.include_router(_r_xo)
router.include_router(_r_yi)
router.include_router(_r_yo)
router.include_router(_r_zi)
router.include_router(_r_zo)
router.include_router(_r_mi)
router.include_router(_r_mo)
