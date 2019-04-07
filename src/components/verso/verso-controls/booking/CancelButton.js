import React from 'react'
import get from 'lodash.get'
import PropTypes from 'prop-types'
import { compose } from 'redux'
import { connect } from 'react-redux'
import { requestData } from 'redux-saga-data'
import { withRouter } from 'react-router-dom'

import Price from '../../../layout/Price'
import { openSharePopin, closeSharePopin } from '../../../../reducers/share'

export const getButton = (label, id, onClick) => (
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

export const getBookingName = booking =>
  booking.stock.resolvedOffer.eventOrThing.name

export const getMediationId = booking => booking.recommendation.mediationId
export const getOfferId = booking => booking.recommendation.offerId
export const getCancelSuccessRedirectFromBookingAndSearch = (
  booking,
  search
) => {
  const offerId = getOfferId(booking)
  const bookingId = get(booking, 'id')
  const mediationId = getMediationId(booking)
  const url = `/decouverte/${offerId}/${mediationId}/cancelled/${bookingId}${search}`
  return url
}

export class RawCancelButton extends React.PureComponent {
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
        getButton('OK', 'popin-cancel-booking-fail-ok', () => {
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
        getButton('Oui', 'popin-cancel-booking-yes', this.onCancelYes(booking)),
        getButton('Non', 'popin-cancel-booking-no', this.onCancelNo()),
      ],
      text: 'Souhaitez vous réellement annuler cette réservation ?',
      title: getBookingName(booking),
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
          {!isCancelled && <i className="icon-ico-check fs24" />}
        </span>
        <span className="pc-ticket-button-label">Annuler</span>
      </button>
    )
  }
}

RawCancelButton.defaultProps = {}

RawCancelButton.propTypes = {
  booking: PropTypes.object.isRequired,
  dispatch: PropTypes.func.isRequired,
  history: PropTypes.object.isRequired,
  isCancelled: PropTypes.bool.isRequired,
  locationSearch: PropTypes.string.isRequired,
  priceValue: PropTypes.number.isRequired,
}

const mapStateToProps = (state, props) => {
  const { booking, history, location } = props
  const locationSearch = location.search
  const priceValue = get(booking, 'stock.price')
  const isCancelled = get(booking, 'isCancelled')
  return {
    history,
    isCancelled,
    locationSearch,
    priceValue,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(RawCancelButton)
