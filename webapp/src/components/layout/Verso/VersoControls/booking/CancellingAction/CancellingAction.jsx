import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

import getIsCancelling from '../../../../../../utils/getIsCancelling'
import Icon from '../../../../Icon/Icon'
import Price from '../../../../Price/Price'

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
    const { offerCanBeCancelled, price } = this.props

    return (
      <button
        className="ticket-action"
        disabled={!offerCanBeCancelled}
        onClick={this.handleCancellingAction}
        type="button"
      >
        <span className="ticket-price ticket-reserved">
          <Price
            free="Gratuit"
            value={price}
          />
          <Icon svg="ico-check" />
        </span>
        <span className="ticket-label">
          {'Annuler'}
        </span>
      </button>
    )
  }
}

CancellingAction.defaultProps = {
  offerCanBeCancelled: true,
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
  offerCanBeCancelled: PropTypes.bool,
  openCancelPopin: PropTypes.func.isRequired,
  price: PropTypes.number.isRequired,
}

export default CancellingAction
