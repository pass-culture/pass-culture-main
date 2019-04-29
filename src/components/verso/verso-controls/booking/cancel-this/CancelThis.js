import React from 'react'
import get from 'lodash.get'
import PropTypes from 'prop-types'
import { requestData } from 'redux-saga-data'

import Price from '../../../../layout/Price'
import { closeSharePopin, openSharePopin } from '../../../../../reducers/share'

class CancelThis extends React.PureComponent {
  buildButton = (label, id, onClick) => (
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

  buildUrlForRedirect = booking => {
    const bookingId = get(booking, 'id')
    const offerId = get(booking.recommendation, 'offerId')

    return `/decouverte/${offerId}/booking/${bookingId}/cancelled`
  }

  onSuccess = booking => {
    const { dispatch, history } = this.props
    dispatch(closeSharePopin())
    history.push(this.buildUrlForRedirect(booking))
  }

  onFailure = (state, request) => {
    const { dispatch } = this.props
    const message = get(request, 'errors.booking') || [
      `Une erreur inconnue s'est produite`,
    ]

    const options = {
      buttons: [
        this.buildButton('OK', 'popin-cancel-booking-fail-ok', () => {
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
        handleFail: this.onFailure,
        handleSuccess: () => this.onSuccess(booking),
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
        this.buildButton(
          'Oui',
          'popin-cancel-booking-yes',
          this.onCancelYes(booking)
        ),
        this.buildButton('Non', 'popin-cancel-booking-no', this.onCancelNo()),
      ],
      text: 'Souhaitez-vous réellement annuler cette réservation ?',
      title: booking.stock.resolvedOffer.name,
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

CancelThis.defaultProps = {}

CancelThis.propTypes = {
  booking: PropTypes.object.isRequired,
  dispatch: PropTypes.func.isRequired,
  history: PropTypes.object.isRequired,
  isCancelled: PropTypes.bool.isRequired,
  priceValue: PropTypes.number.isRequired,
}

export default CancelThis
