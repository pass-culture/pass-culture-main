import datetime
from functools import partial

from flask import render_template
from flask import request
from flask import url_for
import sqlalchemy as sa

from pcapi.core.categories import subcategories_v2
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.utils import date as date_utils
from pcapi.utils.clean_accents import clean_accents

from . import search_utils
from . import utils
from .forms import collective_booking as collective_booking_forms


collective_bookings_blueprint = utils.child_backoffice_blueprint(
    "collective_bookings",
    __name__,
    url_prefix="/collective-bookings",
    permission=perm_models.Permissions.MANAGE_BOOKINGS,
)


def _get_collective_bookings(form: collective_booking_forms.GetCollectiveBookingListForm) -> sa.orm.Query:
    query = (
        educational_models.CollectiveBooking.query.outerjoin(educational_models.CollectiveStock)
        .outerjoin(educational_models.CollectiveOffer)
        .outerjoin(
            educational_models.EducationalInstitution, educational_models.CollectiveBooking.educationalInstitution
        )
        .options(
            sa.orm.joinedload(educational_models.CollectiveBooking.collectiveStock)
            .load_only(educational_models.CollectiveStock.collectiveOfferId)
            .joinedload(educational_models.CollectiveStock.collectiveOffer)
            .load_only(
                educational_models.CollectiveOffer.id,
                educational_models.CollectiveOffer.name,
                educational_models.CollectiveOffer.subcategoryId,
            ),
            sa.orm.joinedload(educational_models.CollectiveBooking.educationalInstitution).load_only(
                educational_models.EducationalInstitution.id, educational_models.EducationalInstitution.name
            ),
            sa.orm.joinedload(educational_models.CollectiveBooking.offerer).load_only(
                offerers_models.Offerer.id, offerers_models.Offerer.name
            ),
            sa.orm.joinedload(educational_models.CollectiveBooking.venue).load_only(
                # for name and link (build_pc_pro_venue_link)
                offerers_models.Venue.id,
                offerers_models.Venue.name,
                offerers_models.Venue.isVirtual,
                offerers_models.Venue.managingOffererId,
            ),
            sa.orm.joinedload(educational_models.CollectiveBooking.pricings)
            .load_only(finance_models.Pricing.amount)
            .joinedload(finance_models.Pricing.cashflows)
            .load_only(finance_models.Cashflow.batchId)
            .joinedload(finance_models.Cashflow.batch)
            .load_only(finance_models.CashflowBatch.label),
        )
    )

    if form.q.data:
        search_query = form.q.data

        if search_query.isnumeric():
            query = query.filter(
                sa.or_(
                    educational_models.CollectiveBooking.id == search_query,
                    educational_models.CollectiveOffer.id == search_query,
                    educational_models.EducationalInstitution.id == search_query,
                )
            )
        else:
            name = search_query.replace(" ", "%").replace("-", "%")
            name = clean_accents(name)
            query = query.filter(
                sa.func.unaccent(educational_models.EducationalInstitution.name).ilike(f"%{name}%"),
            )

    if form.from_date.data:
        from_datetime = date_utils.date_to_localized_datetime(form.from_date.data, datetime.datetime.min.time())
        query = query.filter(educational_models.CollectiveBooking.dateCreated >= from_datetime)

    if form.to_date.data:
        to_datetime = date_utils.date_to_localized_datetime(form.to_date.data, datetime.datetime.max.time())
        query = query.filter(educational_models.CollectiveBooking.dateCreated <= to_datetime)

    if form.offerer.data:
        query = query.filter(educational_models.CollectiveBooking.offererId.in_(form.offerer.data))

    if form.venue.data:
        query = query.filter(educational_models.CollectiveBooking.venueId.in_(form.venue.data))

    if form.category.data:
        query = query.filter(
            educational_models.CollectiveOffer.subcategoryId.in_(
                subcategory.id
                for subcategory in subcategories_v2.ALL_SUBCATEGORIES
                if subcategory.category.id in form.category.data
            )
        )

    if form.status.data:
        query = query.filter(educational_models.CollectiveBooking.status.in_(form.status.data))

    return query.order_by(educational_models.CollectiveBooking.dateCreated.desc())


@collective_bookings_blueprint.route("", methods=["GET"])
def list_collective_bookings() -> utils.BackofficeResponse:
    form = collective_booking_forms.GetCollectiveBookingListForm(request.args)
    if not form.validate():
        return render_template("collective_bookings/list.html", isEAC=True, rows=[], form=form), 400

    if form.is_empty():
        # Empty results when no filter is set
        return render_template("collective_bookings/list.html", rows=[], form=form)

    bookings = _get_collective_bookings(form)

    paginated_bookings = bookings.paginate(  # type: ignore [attr-defined]
        page=int(form.data["page"]),
        per_page=int(form.data["per_page"]),
    )

    next_page = partial(url_for, ".list_collective_bookings", **form.data)
    next_pages_urls = search_utils.pagination_links(next_page, int(form.data["page"]), paginated_bookings.pages)

    form.page.data = 1  # Reset to first page when form is submitted ("Appliquer" clicked)

    if form.offerer.data:
        offerers = (
            offerers_models.Offerer.query.filter(offerers_models.Offerer.id.in_(form.offerer.data))
            .order_by(offerers_models.Offerer.name)
            .with_entities(
                offerers_models.Offerer.id,
                offerers_models.Offerer.name,
                offerers_models.Offerer.siren,
            )
        )
        form.offerer.choices = [(offerer_id, f"{name} ({siren})") for offerer_id, name, siren in offerers]

    if form.venue.data:
        venues = (
            offerers_models.Venue.query.filter(offerers_models.Venue.id.in_(form.venue.data))
            .order_by(offerers_models.Venue.name)
            .with_entities(
                offerers_models.Venue.id,
                offerers_models.Venue.name,
                offerers_models.Venue.siret,
            )
        )
        form.venue.choices = [(venue_id, f"{name} ({siret or 'Pas de SIRET'})") for venue_id, name, siret in venues]

    return render_template(
        "collective_bookings/list.html",
        rows=paginated_bookings,
        form=form,
        next_pages_urls=next_pages_urls,
    )
