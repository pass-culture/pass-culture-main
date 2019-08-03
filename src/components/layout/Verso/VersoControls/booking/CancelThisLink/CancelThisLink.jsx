import React from 'react'
import get from 'lodash.get'
import PropTypes from 'prop-types'
import { requestData } from 'redux-saga-data'

import Price from '../../../../layout/Price'
import { closeSharePopin, openSharePopin } from '../../../../../reducers/share'

class CancelThisLink extends React.PureComponent {
  buildButton = (label, id, onClick) => (
    <button
      className="no-border no-background no-outline is-block py12 is-bold fs14"
      id={id}
      key={label}
      onClick={onClick}
      type="button"
    >
      <span>{label}</span>
    </button>
  )

  buildUrlForRedirect = booking => {
    const bookingId = get(booking, 'id')
    const offerId = get(booking, 'recommendation.offerId')

    return `/decouverte/${offerId}/booking/${bookingId}/cancelled`
  }

  onSuccess = booking => {
    const { dispatch, history } = this.props
    dispatch(closeSharePopin())
    history.push(this.buildUrlForRedirect(booking))
  }

  onFailure = (state, request) => {
    const { dispatch } = this.props
    const { payload } = request
    const message = get(payload, 'errors.booking') || ['Une erreur inconnue s’est produite']

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
    const title = get(booking, 'stock.resolvedOffer.name')

    const options = {
      buttons: [
        this.buildButton('Oui', 'popin-cancel-booking-yes', this.onCancelYes(booking)),
        this.buildButton('Non', 'popin-cancel-booking-no', this.onCancelNo()),
      ],
      text: 'Souhaitez-vous réellement annuler cette réservation ?',
      title,
    }
    dispatch(openSharePopin(options))
  }

  handleOnClick = (isFinished, booking) => () => !isFinished && this.openCancelPopin(booking)

  render() {
    const { booking, isCancelled, isFinished, priceValue } = this.props

    return (
      <button
        className="flex-columns no-border no-background"
        disabled={isFinished}
        id="verso-cancel-booking-button"
        onClick={this.handleOnClick(isFinished, booking)}
        type="button"
      >
        <span className="pc-ticket-button-price reserved">
          <Price
            free="Gratuit"
            value={priceValue}
          />
          {!isCancelled && (
            <i
              className="icon-ico-check fs24"
              id="verso-cancel-booking-button-reserved"
            />
          )}
        </span>
        <span className="pc-ticket-button-label">{'Annuler'}</span>
      </button>
    )
  }
}

CancelThisLink.defaultProps = {
  isFinished: false,
}

CancelThisLink.propTypes = {
  booking: PropTypes.shape().isRequired,
  dispatch: PropTypes.func.isRequired,
  history: PropTypes.shape().isRequired,
  isCancelled: PropTypes.bool.isRequired,
  isFinished: PropTypes.bool,
  priceValue: PropTypes.number.isRequired,
}

export default CancelThisLink
