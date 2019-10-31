import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

import Price from '../../../../Price/Price'
import getIsCancelling from '../../../../../../helpers/getIsCancelling'

class CancellingAction extends PureComponent {
  componentDidMount() {
    const { booking, match, offer, openCancelPopin } = this.props
    const { id: bookingId } = booking
    const { name: offerName, id: offerId } = offer
    const isCancelling = getIsCancelling(match)

    if (isCancelling) {
      openCancelPopin(bookingId, offerName, offerId)
    }
  }

  componentDidUpdate(prevProps) {
    const { booking, match, offer, openCancelPopin } = this.props
    const { id: bookingId } = booking
    const { name: offerName, id: offerId } = offer
    const isCancelling = getIsCancelling(match)
    const previousIsCancelling = getIsCancelling(prevProps.match)

    if (isCancelling && !previousIsCancelling) {
      openCancelPopin(bookingId, offerName, offerId)
    }
  }

  handleCancellingAction = () => {
    const { cancellingUrl, history } = this.props

    history.push(cancellingUrl)
  }

  render() {
    const { price } = this.props

    return (
      <button
        className="ticket-action"
        onClick={this.handleCancellingAction}
        type="button"
      >
        <span className="ticket-price ticket-reserved">
          <Price
            free="Gratuit"
            value={price}
          />
          <i className="icon-ico-check ticket-reserved-icon" />
        </span>
        <span className="ticket-label">
          {'Annuler'}
        </span>
      </button>
    )
  }
}

CancellingAction.propTypes = {
  booking: PropTypes.shape().isRequired,
  cancellingUrl: PropTypes.string.isRequired,
  history: PropTypes.shape({
    push: PropTypes.func.isRequired,
  }).isRequired,
  location: PropTypes.shape({
    pathname: PropTypes.string.isRequired,
    search: PropTypes.string.isRequired,
  }).isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      bookings: PropTypes.string,
      bookingId: PropTypes.string,
      cancellation: PropTypes.string,
    }).isRequired,
  }).isRequired,
  offer: PropTypes.shape().isRequired,
  openCancelPopin: PropTypes.func.isRequired,
  price: PropTypes.number.isRequired,
}

export default CancellingAction
