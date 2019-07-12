import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'

import Price from '../../../../layout/Price'
import VersoPriceFormatter from '../verso-price-formatter/VersoPriceFormatter'

class BookThisLink extends Component {
  formatOutputPrice = ([startingPrice, endingPrice], devise) => (
    <VersoPriceFormatter
      devise={devise}
      endingPrice={endingPrice}
      startingPrice={startingPrice}
    />
  )

  render() {
    const { isFinished, linkDestination, priceValue } = this.props

    return (
      <Link
        className="flex-columns is-bold is-white-text fs18"
        disabled={isFinished}
        id="verso-booking-button"
        to={linkDestination}
      >
        <Price
          className="pc-ticket-button-price flex-columns items-center"
          format={this.formatOutputPrice}
          free="Gratuit"
          value={priceValue}
        />
        <span className="pc-ticket-button-label">{'J’y vais !'}</span>
      </Link>
    )
  }
}

BookThisLink.defaultProps = {
  isFinished: false,
}

BookThisLink.propTypes = {
  isFinished: PropTypes.bool,
  linkDestination: PropTypes.string.isRequired,
  priceValue: PropTypes.arrayOf(PropTypes.number).isRequired,
}

export default BookThisLink
