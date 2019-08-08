import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'

import VersoPriceFormatter from '../VersoPriceFormatter/VersoPriceFormatter'
import Price from '../../../../Price'

class BookThisLink extends Component {
  formatOutputPrice = ([startingPrice, endingPrice], devise) => (
    <VersoPriceFormatter
      devise={devise}
      endingPrice={endingPrice}
      startingPrice={startingPrice}
    />
  )

  render() {
    const { isFinished, priceRange, destinationLink } = this.props
    return (
      <Link
        className="flex-columns is-bold is-white-text fs18"
        disabled={isFinished}
        id="verso-booking-button"
        to={destinationLink}
      >
        <Price
          className="pc-ticket-button-price flex-columns items-center"
          format={this.formatOutputPrice}
          free="Gratuit"
          value={priceRange}
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
  destinationLink: PropTypes.string.isRequired,
  isFinished: PropTypes.bool,
  priceRange: PropTypes.arrayOf(PropTypes.number.isRequired).isRequired,
}

export default BookThisLink
