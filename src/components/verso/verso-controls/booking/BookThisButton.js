/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'

import Price from '../../../layout/Price'
import VersoPriceFormatter from './VersoPriceFormatter'

export const formatOutputPrice = (prices, devise) => {
  const [startingPrice, endingPrice] = prices
  return (
    <VersoPriceFormatter
      devise={devise}
      endingPrice={endingPrice}
      startingPrice={startingPrice}
    />
  )
}

class BookThisButton extends React.PureComponent {
  render() {
    const { destinationPathname, destinationSearch, priceValue } = this.props
    return (
      <Link
        to={{
          pathname: destinationPathname,
          search: destinationSearch,
        }}
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
  }
}

BookThisButton.propTypes = {
  destinationPathname: PropTypes.string.isRequired,
  destinationSearch: PropTypes.string.isRequired,
  priceValue: PropTypes.array.isRequired,
}

export default BookThisButton
