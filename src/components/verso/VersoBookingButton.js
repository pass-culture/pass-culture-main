/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import get from 'lodash.get'
import React from 'react'
import { connect } from 'react-redux'
import { Link, withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import Price from '../layout/Price'
import Finishable from '../layout/Finishable'
import { isRecommendationFinished } from '../../helpers'
import { openSharePopin, closeSharePopin } from '../../reducers/share'
import { selectBookings } from '../../selectors/selectBookings'
import currentRecommendation from '../../selectors/currentRecommendation'

export const getButton = (label, onClick) => (
  <button
    className="no-border no-background no-outline is-block py12 is-bold fs14"
    key={label}
    onClick={onClick}
    type="button"
  >
    <span>{label}</span>
  </button>
)

export const getBookingName = booking =>
  booking.stock.resolvedOffer.eventOrThing.name

export const getMediationId = booking => booking.recommendation.mediationId
export const getOfferId = booking => booking.recommendation.offerId
export const getCancelSuccessRedirectFromBookingAndSearch = (
  booking,
  search
) => {
  const offerId = getOfferId(booking)
  const mediationId = getMediationId(booking)
  const url = `/decouverte/${offerId}/${mediationId}/cancelled/${
    booking.id
  }${search}`
  return url
}

class VersoBookingButton extends React.PureComponent {
  renderBookingLink = () => {
    const { location, offer, url } = this.props
    const { search } = location
    const priceValue = get(offer, 'price') || get(offer, 'displayPrice')
    const to = `${url}/booking${search}`

    return (
      <Link
        to={to}
        id="verso-booking-button"
        className="button is-primary is-medium"
      >
        <Price free="——" value={priceValue} />
        <span>J&apos;y vais!</span>
      </Link>
    )
  }

  onCancelSuccess = booking => {
    const { dispatch, history, location } = this.props
    const { search } = location
    dispatch(closeSharePopin())

    const redirect = getCancelSuccessRedirectFromBookingAndSearch(
      booking,
      search
    )
    history.push(redirect)
  }

  onCancelFailure = (state, request) => {
    const { dispatch } = this.props
    const message = get(request, 'errors.booking') || [
      'Une erreur inconnue sest produite',
    ]

    const options = {
      buttons: [
        getButton('OK', () => {
          dispatch(closeSharePopin())
        }),
      ],
      text: message.join('\n'),
      title: 'Annulation impossible',
    }
    dispatch(openSharePopin(options))
  }

  onCancelYes = booking => () => {
    const { dispatch } = this.props
    dispatch(
      requestData({
        apiPath: `/bookings/${booking.id}`,
        body: { isCancelled: true },
        handleFail: this.onCancelFailure,
        handleSuccess: () => this.onCancelSuccess(booking),
        method: 'PATCH',
      })
    )
  }

  onCancelNo = () => () => {
    const { dispatch } = this.props
    dispatch(closeSharePopin())
  }

  openCancelPopin = booking => {
    const { dispatch } = this.props
    const options = {
      buttons: [
        getButton('Oui', this.onCancelYes(booking)),
        getButton('Non', this.onCancelNo()),
      ],
      text: 'Souhaitez vous réellement annuler cette réservation ?',
      title: getBookingName(booking),
    }
    dispatch(openSharePopin(options))
  }

  renderOfflineCancelableButton = booking => (
    <button
      id="verso-cancel-booking-button"
      type="button"
      className="cancel-button"
      onClick={() => this.openCancelPopin(booking)}
    >
      Annuler
    </button>
  )

  renderOfflineNotCancelableButton = () => (
    <Link
      id="verso-already-booked-button"
      to="/reservations"
      className="button is-primary is-medium"
    >
      Réservé
    </Link>
  )

  renderOfflineButton = booking => {
    if (booking.isUserCancellable) {
      return this.renderOfflineCancelableButton(booking)
    }

    return this.renderOfflineNotCancelableButton()
  }

  renderOnlineButton = () => {
    const { booking } = this.props
    const onlineOfferUrl = get(booking, 'completedUrl')
    return (
      <a
        id="verso-online-booked-button"
        href={`${onlineOfferUrl}`}
        target="_blank"
        rel="noopener noreferrer"
        className="button is-primary is-medium"
      >
        Accéder
      </a>
    )
  }

  render() {
    const { booking, isFinished } = this.props
    const onlineOfferUrl = get(booking, 'completedUrl')
    return (
      <React.Fragment>
        {booking && onlineOfferUrl && this.renderOnlineButton()}
        {booking && !onlineOfferUrl && this.renderOfflineButton(booking)}
        {!booking && !isFinished && this.renderBookingLink()}
        {!booking && isFinished && (
          <Finishable finished>{this.renderBookingLink()}</Finishable>
        )}
      </React.Fragment>
    )
  }
}

VersoBookingButton.defaultProps = {
  booking: null,
  isFinished: false,
  offer: null,
}

VersoBookingButton.propTypes = {
  booking: PropTypes.object,
  dispatch: PropTypes.func.isRequired,
  history: PropTypes.object.isRequired,
  isFinished: PropTypes.bool,
  location: PropTypes.object.isRequired,
  offer: PropTypes.object,
  url: PropTypes.string.isRequired,
}

const mapStateToProps = (state, { match }) => {
  const { params, url } = match
  const { mediationId, offerId } = params
  const recommendation = currentRecommendation(state, offerId, mediationId)
  const isFinished = isRecommendationFinished(recommendation, offerId)
  // NOTE -> on ne peut pas faire confiance a bookingsIds
  // bookingsIds n'est pas mis à jour avec le state
  const stocks = get(recommendation, 'offer.stocks')
  const stockIds = (stocks || []).map(o => o.id)
  const bookings = selectBookings(state)
  const booking = bookings.find(b => stockIds.includes(b.stockId))
  return {
    booking,
    isFinished,
    offer: recommendation && recommendation.offer,
    url: url.replace(/\/$/, ''),
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(VersoBookingButton)
