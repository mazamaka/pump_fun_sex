from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import UniqueConstraint, Column, JSON, String
from sqlmodel import SQLModel, Field


class TokenEventBase(SQLModel):
    signature: str = Field(index=True)
    mint: Optional[str] = None
    trader_public_key: Optional[str] = None
    tx_type: Optional[str] = None
    initial_buy: Optional[float] = None
    sol_amount: Optional[float] = None
    bonding_curve_key: Optional[str] = None
    v_tokens_in_bonding_curve: Optional[float] = None
    v_sol_in_bonding_curve: Optional[float] = None
    market_cap_sol: Optional[float] = None
    name: Optional[str] = None
    symbol: Optional[str] = None
    uri: Optional[str] = None
    pool: Optional[str] = None
    raw: Optional[dict] = Field(default=None, sa_column=Column(JSON))


class TokenEvent(TokenEventBase, table=True):
    __tablename__ = "token_events"
    __table_args__ = (
        UniqueConstraint("signature", name="uq_token_event_signature"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class TokenEventRead(TokenEventBase):
    id: int
    created_at: datetime
