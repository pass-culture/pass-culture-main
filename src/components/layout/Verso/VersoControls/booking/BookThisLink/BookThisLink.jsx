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

  getLinkDestination = () => {
    const { match, location } = this.props
    const { search } = location
    const { params, url } = match
    if (params.bookings) {
      return url
    }
    const isValid = url && typeof url === 'string'
    if (!isValid) {
      throw new Error('Invalid url parameter')
    }
    let formattedUrl = url
    return `${formattedUrl}/reservations${search || ''}`
  }

  render() {
    const { isFinished, priceRange } = this.props
    return (
      <Link
        className="flex-columns is-bold is-white-text fs18"
        disabled={isFinished}
        id="verso-booking-button"
        to={this.getLinkDestination()}
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
  isFinished: false
}

BookThisLink.propTypes = {
  isFinished: PropTypes.bool,
  location: PropTypes.shape({
    search: PropTypes.string.isRequired,
  }).isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      bookings: PropTypes.string
    }).isRequired,
    url: PropTypes.string.isRequired,
  }).isRequired,
  priceRange: PropTypes.arrayOf(PropTypes.number.isRequired).isRequired
}

export default BookThisLink
