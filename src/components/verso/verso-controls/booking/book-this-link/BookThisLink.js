import React from 'react'
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'

import Price from '../../../../layout/Price'
import VersoPriceFormatter from '../verso-price-formatter/VersoPriceFormatter'

export const formatOutputPrice = ([startingPrice, endingPrice], devise) => (
  <VersoPriceFormatter
    devise={devise}
    endingPrice={endingPrice}
    startingPrice={startingPrice}
  />
)

const BookThisLink = ({ linkDestination, priceValue }) => (
  <Link
    to={linkDestination}
    id="verso-booking-button"
    className="flex-columns is-bold is-white-text fs18"
  >
    <Price
      free="Gratuit"
      className="pc-ticket-button-price flex-columns items-center"
      value={priceValue}
      format={formatOutputPrice}
    />
    <span className="pc-ticket-button-label">J&apos;y vais!</span>
  </Link>
)

BookThisLink.propTypes = {
  linkDestination: PropTypes.string.isRequired,
  priceValue: PropTypes.array.isRequired,
}

export default BookThisLink
