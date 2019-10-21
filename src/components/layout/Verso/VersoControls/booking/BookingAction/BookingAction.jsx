import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

import Price from '../../../../Price/Price'

class BookingAction extends PureComponent {
  handleBookingAction = () => {
    const { bookingUrl, history } = this.props

    history.push(bookingUrl)
  }

  render() {
    const { isNotBookable, priceRange } = this.props

    return (
      <button
        className="ticket-action"
        disabled={isNotBookable}
        onClick={this.handleBookingAction}
        type="button"
      >
        <Price
          className="ticket-price"
          free="Gratuit"
          value={priceRange}
        />
        <span className="ticket-label">{'J’y vais !'}</span>
      </button>
    )
  }
}

BookingAction.defaultProps = {
  isNotBookable: false,
}

BookingAction.propTypes = {
  bookingUrl: PropTypes.string.isRequired,
  history: PropTypes.shape().isRequired,
  isNotBookable: PropTypes.bool,
  priceRange: PropTypes.arrayOf(PropTypes.number.isRequired).isRequired,
}

export default BookingAction
