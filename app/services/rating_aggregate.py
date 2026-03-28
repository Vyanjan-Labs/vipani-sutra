from sqlalchemy import func as sql_func
from sqlalchemy.orm import Session

from app.models.rating import Rating


def rating_summary_for_user(db: Session, user_id: int) -> dict:
    """Aggregates for ratings received as seller vs as buyer (to_user_id = this user)."""
    as_seller = (
        db.query(sql_func.avg(Rating.stars), sql_func.count(Rating.id))
        .filter(
            Rating.to_user_id == user_id,
            Rating.reputation_scope == "seller",
        )
        .one()
    )
    as_buyer = (
        db.query(sql_func.avg(Rating.stars), sql_func.count(Rating.id))
        .filter(
            Rating.to_user_id == user_id,
            Rating.reputation_scope == "buyer",
        )
        .one()
    )
    s_avg, s_cnt = as_seller[0], int(as_seller[1] or 0)
    b_avg, b_cnt = as_buyer[0], int(as_buyer[1] or 0)
    return {
        "as_seller_avg": round(float(s_avg), 2) if s_avg is not None else None,
        "as_seller_count": s_cnt,
        "as_buyer_avg": round(float(b_avg), 2) if b_avg is not None else None,
        "as_buyer_count": b_cnt,
    }
