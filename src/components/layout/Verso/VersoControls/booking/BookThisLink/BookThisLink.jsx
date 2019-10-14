import React from 'react'
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'

import Price from '../../../../Price/Price'

const BookThisLink = ({ isNotBookable, priceRange, destinationLink }) => (
  <Link
    className="flex-columns"
    disabled={isNotBookable}
    id="verso-booking-button"
    to={destinationLink}
  >
    <Price
      className="pc-ticket-button-price flex-columns items-center"
      free="Gratuit"
      value={priceRange}
    />
    <span className="pc-ticket-button-label">{'J’y vais !'}</span>
  </Link>
)

BookThisLink.defaultProps = {
  isNotBookable: false,
}

BookThisLink.propTypes = {
  destinationLink: PropTypes.string.isRequired,
  isNotBookable: PropTypes.bool,
  priceRange: PropTypes.arrayOf(PropTypes.number.isRequired).isRequired,
}

export default BookThisLink
