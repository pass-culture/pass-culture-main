import React from 'react'
import get from 'lodash.get'
import PropTypes from 'prop-types'
import { requestData } from 'redux-saga-data'

import Price from '../../../layout/Price'
import { openSharePopin, closeSharePopin } from '../../../../reducers/share'

class CancelButton extends React.PureComponent {
  getButton = (label, id, onClick) => (
    <button
      id={id}
      className="no-border no-background no-outline is-block py12 is-bold fs14"
      key={label}
      onClick={onClick}
      type="button"
    >
      <span>{label}</span>
    </button>
  )

  getBookingName = booking => booking.stock.resolvedOffer.name

  getMediationId = booking => booking.recommendation.mediationId

  getOfferId = booking => booking.recommendation.offerId

  getCancelSuccessRedirectFromBookingAndSearch = (booking, search) => {
    const offerId = this.getOfferId(booking)
    const mediationId = this.getMediationId(booking)
    const url = `/decouverte/${offerId}/${mediationId}/${search}`
    return url
  }

  onCancelSuccess = booking => {
    const { dispatch, history, locationSearch } = this.props
    dispatch(closeSharePopin())

    const redirect = this.getCancelSuccessRedirectFromBookingAndSearch(
      booking,
      locationSearch
    )
    history.push(redirect)
  }

  onCancelFailure = (state, request) => {
    const { dispatch } = this.props
    const message = get(request, 'errors.booking') || [
      `Une erreur inconnue s'est produite`,
    ]

    const options = {
      buttons: [
        this.getButton('OK', 'popin-cancel-booking-fail-ok', () => {
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
        this.getButton(
          'Oui',
          'popin-cancel-booking-yes',
          this.onCancelYes(booking)
        ),
        this.getButton('Non', 'popin-cancel-booking-no', this.onCancelNo()),
      ],
      text: 'Souhaitez-vous réellement annuler cette réservation ?',
      title: this.getBookingName(booking),
    }
    dispatch(openSharePopin(options))
  }

  render() {
    const { booking, isCancelled, priceValue } = this.props
    return (
      <button
        id="verso-cancel-booking-button"
        type="button"
        className="flex-columns no-border no-background"
        onClick={() => this.openCancelPopin(booking)}
      >
        <span className="pc-ticket-button-price reserved">
          <Price free="Gratuit" value={priceValue} />
          {!isCancelled && (
            <i
              id="verso-cancel-booking-button-reserved"
              className="icon-ico-check fs24"
            />
          )}
        </span>
        <span className="pc-ticket-button-label">Annuler</span>
      </button>
    )
  }
}

CancelButton.defaultProps = {}

CancelButton.propTypes = {
  booking: PropTypes.object.isRequired,
  dispatch: PropTypes.func.isRequired,
  history: PropTypes.object.isRequired,
  isCancelled: PropTypes.bool.isRequired,
  locationSearch: PropTypes.string.isRequired,
  priceValue: PropTypes.number.isRequired,
}

export default CancelButton
