import React from 'react'
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'

import Price from '../../../layout/Price'

const BookThisButton = ({ linkDestination, priceValue }) => (
  <Link
    to={linkDestination}
    id="verso-booking-button"
    className="button-with-price flex-columns is-bold is-white-text fs18"
  >
    <Price className="px12 py8" free="Gratuit" value={priceValue} />
    <hr className="dotted-left-2x-white no-margin" />
    <span className="button-label px12 py8">J&apos;y vais!</span>
  </Link>
)

BookThisButton.propTypes = {
  linkDestination: PropTypes.string.isRequired,
  priceValue: PropTypes.array.isRequired,
}

export default BookThisButton
