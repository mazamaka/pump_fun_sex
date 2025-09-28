from typing import Optional, List

from sqlmodel import Session, select

from .db import engine
from .models import TokenEvent


class TokenEventRepository:
    def upsert_from_event(self, event: dict) -> TokenEvent:
        signature = event.get("signature")
        if not signature:
            raise ValueError("Event missing signature")

        with Session(engine) as session:
            existing = session.exec(
                select(TokenEvent).where(TokenEvent.signature == signature)
            ).first()
            if existing:
                return existing

            obj = TokenEvent(
                signature=signature,
                mint=event.get("mint"),
                trader_public_key=event.get("traderPublicKey"),
                tx_type=event.get("txType"),
                initial_buy=event.get("initialBuy"),
                sol_amount=event.get("solAmount"),
                bonding_curve_key=event.get("bondingCurveKey"),
                v_tokens_in_bonding_curve=event.get("vTokensInBondingCurve"),
                v_sol_in_bonding_curve=event.get("vSolInBondingCurve"),
                market_cap_sol=event.get("marketCapSol"),
                name=event.get("name"),
                symbol=event.get("symbol"),
                uri=event.get("uri"),
                pool=event.get("pool"),
                raw=event,
            )
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj

    def list(self, limit: int = 50, offset: int = 0) -> List[TokenEvent]:
        with Session(engine) as session:
            stmt = (
                select(TokenEvent)
                .order_by(TokenEvent.id.desc())
                .limit(limit)
                .offset(offset)
            )
            return list(session.exec(stmt))

    def get_by_signature(self, signature: str) -> Optional[TokenEvent]:
        with Session(engine) as session:
            return session.exec(
                select(TokenEvent).where(TokenEvent.signature == signature)
            ).first()
