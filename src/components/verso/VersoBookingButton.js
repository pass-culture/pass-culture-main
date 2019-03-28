/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import get from 'lodash.get'
import React from 'react'
import { connect } from 'react-redux'
import { Link, withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import Finishable from '../layout/Finishable'
import { isRecommendationFinished } from '../../helpers'
import { openSharePopin, closeSharePopin } from '../../reducers/share'
import { selectBookings } from '../../selectors/selectBookings'
import currentRecommendation from '../../selectors/currentRecommendation'
import BookThisButtonContainer from './verso-buttons/BookThisButtonContainer'

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
  renderBookingThisButton = () => {
    const { isFinished } = this.props
    return (
      <Finishable finished={isFinished}>
        <BookThisButtonContainer />
      </Finishable>
    )
  }

  onCancelSuccess = booking => {
    const { dispatch, history, locationSearch } = this.props
    dispatch(closeSharePopin())

    const redirect = getCancelSuccessRedirectFromBookingAndSearch(
      booking,
      locationSearch
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
      className="cancel-button is-bold fs18 px10 py5"
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
    const { onlineOfferUrl } = this.props
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
    const { booking, onlineOfferUrl } = this.props
    return (
      <React.Fragment>
        {booking && onlineOfferUrl && this.renderOnlineButton()}
        {booking && !onlineOfferUrl && this.renderOfflineButton(booking)}
        {!booking && this.renderBookingThisButton()}
      </React.Fragment>
    )
  }
}

VersoBookingButton.defaultProps = {
  booking: null,
  isFinished: false,
  onlineOfferUrl: null,
}

VersoBookingButton.propTypes = {
  booking: PropTypes.object,
  dispatch: PropTypes.func.isRequired,
  history: PropTypes.object.isRequired,
  isFinished: PropTypes.bool,
  locationSearch: PropTypes.string.isRequired,
  onlineOfferUrl: PropTypes.string,
}

const mapStateToProps = (state, { match, location }) => {
  const { mediationId, offerId } = match.params
  const { search: locationSearch } = location
  const recommendation = currentRecommendation(state, offerId, mediationId)
  const isFinished = isRecommendationFinished(recommendation, offerId)
  // NOTE -> on ne peut pas faire confiance a bookingsIds
  // bookingsIds n'est pas mis à jour avec le state
  const stocks = get(recommendation, 'offer.stocks')
  const stockIds = (stocks || []).map(o => o.id)
  const bookings = selectBookings(state)
  const booking = bookings.find(b => stockIds.includes(b.stockId))
  const onlineOfferUrl = get(booking, 'completedUrl')
  return {
    booking,
    isFinished,
    locationSearch,
    onlineOfferUrl,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(VersoBookingButton)
