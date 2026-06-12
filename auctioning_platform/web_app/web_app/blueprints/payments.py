from flask import Blueprint, Response, flash, make_response, redirect, render_template, request, url_for
from flask_login import current_user
import flask_injector
import injector
from uuid import UUID

from payments import PaymentsFacade
from web_app.presenters import PaymentPresenter

payments_blueprint = Blueprint("payments_blueprint", __name__)

@payments_blueprint.route("/")
def index(payments_facade: PaymentsFacade, presenter: PaymentPresenter) -> str:
    if not current_user.is_authenticated:
        return redirect(url_for("security.login"))
    
    pending_payments = payments_facade.get_pending_payments(current_user.id)
    view_models = presenter.list_to_view_model(pending_payments)
    return render_template("payments/index.html", payments=view_models)

@payments_blueprint.route("/<uuid:payment_uuid>/pay", methods=["POST"])
def pay(payment_uuid: UUID, payments_facade: PaymentsFacade) -> Response:
    if not current_user.is_authenticated:
        return make_response("Unauthorized", 401)
    
    # In a real app, 'token' would come from Stripe/etc. 
    # Here we just mock it.
    try:
        payments_facade.charge(payment_uuid, current_user.id, "mock-token")
        flash("Payment successful!", "success")
    except Exception as e:
        flash(f"Payment failed: {str(e)}", "error")
        
    return redirect(url_for("payments_blueprint.index"))
