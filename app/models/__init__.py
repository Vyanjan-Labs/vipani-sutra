# Import all models so Base.metadata.create_all registers every table.
from app.models.buyer_profile import BuyerProfile  # noqa: F401
from app.models.listing import Listing  # noqa: F401
from app.models.rating import Rating  # noqa: F401
from app.models.seller_profile import SellerProfile  # noqa: F401
from app.models.user import User  # noqa: F401
