from dataclasses import dataclass
from datetime import datetime
from typing import Any, List
from auctions.application.queries import AuctionDto

@dataclass
class AuctionViewModel:
    id: int
    title: str
    current_price: str
    starting_price: str
    ends_at: str
    is_ended: bool
    url: str

class AuctionPresenter:
    def list_to_view_model(self, dtos: List[AuctionDto]) -> List[AuctionViewModel]:
        return [self.to_view_model(dto) for dto in dtos]

    def to_view_model(self, dto: AuctionDto) -> AuctionViewModel:
        now = datetime.now()
        return AuctionViewModel(
            id=dto.id,
            title=dto.title,
            current_price=f"${dto.current_price.amount:,.2f}",
            starting_price=f"${dto.starting_price.amount:,.2f}",
            ends_at=dto.ends_at.strftime("%B %d, %Y %H:%M"),
            is_ended=dto.ends_at < now,
            url=f"/auctions/ui/{dto.id}"
        )

@dataclass
class PaymentViewModel:
    uuid: str
    description: str
    amount: str
    status: str

class PaymentPresenter:
    def list_to_view_model(self, dtos: List[Any]) -> List[PaymentViewModel]:
        return [self.to_view_model(dto) for dto in dtos]

    def to_view_model(self, dto: Any) -> PaymentViewModel:
        return PaymentViewModel(
            uuid=str(dto.uuid),
            description=dto.description,
            amount=f"${dto.amount.amount:,.2f}",
            status=dto.status
        )
