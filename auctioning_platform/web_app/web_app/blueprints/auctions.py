from datetime import datetime
from flask import Blueprint, Response, abort, flash, jsonify, make_response, redirect, render_template, request, url_for
import flask_injector
from flask_login import current_user
import injector

from foundation.value_objects import Money
from foundation.value_objects.currency import USD
from auctions import (
    AuctionId,
    GetActiveAuctions,
    GetSingleAuction,
    BeginningAuction,
    BeginningAuctionInputDto,
    EndingAuction,
    EndingAuctionInputDto,
    WithdrawingBids,
    WithdrawingBidsInputDto,
    PlacingBid,
    PlacingBidInputDto,
    PlacingBidOutputBoundary,
    PlacingBidOutputDto,
)
from web_app.presenters import AuctionPresenter, PaymentPresenter
from web_app.serialization.dto import get_dto

auctions_blueprint = Blueprint("auctions_blueprint", __name__)


class AuctionsWeb(injector.Module):
    @injector.provider
    @flask_injector.request
    def placing_bid_output_boundary(self) -> PlacingBidOutputBoundary:
        if request.endpoint == "auctions_blueprint.place_bid_ui":
            return PlacingBidUiPresenter()
        return PlacingBidApiPresenter()

    @injector.provider
    def auction_presenter(self) -> AuctionPresenter:
        return AuctionPresenter()

    @injector.provider
    def payment_presenter(self) -> PaymentPresenter:
        return PaymentPresenter()


@auctions_blueprint.route("/")
def auctions_list(query: GetActiveAuctions) -> Response:
    return make_response(jsonify(query.query()))


@auctions_blueprint.route("/ui")
def auctions_list_ui(query: GetActiveAuctions, presenter: AuctionPresenter) -> str:
    dtos = query.query()
    view_models = presenter.list_to_view_model(dtos)
    return render_template("auctions/list.html", auctions=view_models)


@auctions_blueprint.route("/<int:auction_id>")
def single_auction(auction_id: int, query: GetSingleAuction) -> Response:
    return make_response(jsonify(query.query(auction_id)))


@auctions_blueprint.route("/ui/<int:auction_id>")
def single_auction_ui(auction_id: int, query: GetSingleAuction, presenter: AuctionPresenter) -> str:
    dto = query.query(auction_id)
    view_model = presenter.to_view_model(dto)
    return render_template("auctions/detail.html", auction=view_model)


@auctions_blueprint.route("/create")
def create_auction_ui() -> str:
    if not current_user.is_authenticated:
        abort(403)
    return render_template("auctions/create.html")


@auctions_blueprint.route("/create_ui", methods=["POST"])
def create_auction_ui_post(beginning_auction_uc: BeginningAuction) -> Response:
    if not current_user.is_authenticated:
        abort(403)

    from random import randint
    ends_at = datetime.strptime(request.form["ends_at"], "%Y-%m-%dT%H:%M")
    input_dto = BeginningAuctionInputDto(
        auction_id=randint(1, 1000000), # Simple ID generation for now
        title=request.form["title"],
        starting_price=Money(USD, request.form["starting_price"]),
        ends_at=ends_at
    )
    beginning_auction_uc.execute(input_dto)
    flash(f"Auction '{input_dto.title}' started successfully!", "success")
    return redirect(url_for("auctions_blueprint.auctions_list_ui"))


@auctions_blueprint.route("/<int:auction_id>/close", methods=["POST"])
def close_auction(auction_id: int, ending_auction_uc: EndingAuction) -> Response:
    if not current_user.is_authenticated:
        abort(403)
    
    ending_auction_uc.execute(EndingAuctionInputDto(auction_id))
    flash("Auction closed successfully!", "success")
    return redirect(url_for("auctions_blueprint.single_auction_ui", auction_id=auction_id))


@auctions_blueprint.route("/<int:auction_id>/withdraw_bid", methods=["POST"])
def withdraw_bid(auction_id: int, withdrawing_bids_uc: WithdrawingBids) -> Response:
    if not current_user.is_authenticated:
        abort(403)
    
    bid_id = int(request.form["bid_id"])
    withdrawing_bids_uc.execute(WithdrawingBidsInputDto(auction_id, [bid_id]))
    flash("Bid withdrawn successfully!", "success")
    return redirect(url_for("auctions_blueprint.single_auction_ui", auction_id=auction_id))


@auctions_blueprint.route("/<int:auction_id>/bids", methods=["POST"])
def place_bid(auction_id: AuctionId, placing_bid_uc: PlacingBid, presenter: PlacingBidOutputBoundary) -> Response:
    if not current_user.is_authenticated:
        abort(403)

    dto = get_dto(request, PlacingBidInputDto, context={"auction_id": auction_id, "bidder_id": current_user.id})

    placing_bid_uc.execute(dto)
    return presenter.response  # type: ignore


@auctions_blueprint.route("/<int:auction_id>/bid_ui", methods=["POST"])
def place_bid_ui(auction_id: AuctionId, placing_bid_uc: PlacingBid, presenter: PlacingBidOutputBoundary) -> Response:
    if not current_user.is_authenticated:
        abort(403)

    amount = Money(USD, request.form["amount"])
    dto = PlacingBidInputDto(bidder_id=current_user.id, auction_id=auction_id, amount=amount)

    placing_bid_uc.execute(dto)
    return presenter.response  # type: ignore


class PlacingBidApiPresenter(PlacingBidOutputBoundary):
    response: Response

    def present(self, output_dto: PlacingBidOutputDto) -> None:
        message = (
            "Hooray! You are a winner"
            if output_dto.is_winner
            else f"Your bid is too low. Current price is {output_dto.current_price}"
        )
        self.response = make_response(jsonify({"message": message}))


class PlacingBidUiPresenter(PlacingBidOutputBoundary):
    response: Response

    def present(self, output_dto: PlacingBidOutputDto) -> None:
        if output_dto.is_winner:
            flash("Hooray! You are the current winner!", "success")
        else:
            flash(f"Your bid was too low. The current price is ${output_dto.current_price.amount:,.2f}", "error")
        
        self.response = redirect(url_for("auctions_blueprint.single_auction_ui", auction_id=request.view_args["auction_id"]))
