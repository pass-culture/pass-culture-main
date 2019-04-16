/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import get from 'lodash.get'
import React from 'react'
import { Link } from 'react-router-dom'
import { requestData } from 'redux-saga-data'

import Finishable from '../../../layout/Finishable'
import { closeSharePopin, openSharePopin } from '../../../../reducers/share'
import BookThisButtonContainer from '../book-this-button/BookThisButtonContainer'

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
  getBookingName = booking => booking.stock.resolvedOffer.eventOrThing.name

  getButton = (label, onClick) => (
    <button
      className="no-border no-background no-outline is-block py12 is-bold fs14"
      key={label}
      onClick={onClick}
      type="button"
    >
      <span>{label}</span>
    </button>
  )

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
      "Une erreur inconnue s'est produite",
    ]

    const options = {
      buttons: [
        this.getButton('OK', () => {
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
        this.getButton('Oui', this.onCancelYes(booking)),
        this.getButton('Non', this.onCancelNo()),
      ],
      text: 'Souhaitez-vous réellement annuler cette réservation ?',
      title: this.getBookingName(booking),
    }
    dispatch(openSharePopin(options))
  }

  renderOfflineButton = booking => {
    if (booking.isUserCancellable) {
      return this.renderOfflineCancelableButton(booking)
    }

    return this.renderOfflineNotCancelableButton()
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

export default VersoBookingButton
