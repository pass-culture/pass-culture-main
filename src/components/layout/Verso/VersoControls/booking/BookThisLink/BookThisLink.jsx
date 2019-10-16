import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import { Link } from 'react-router-dom'

import Price from '../../../../Price/Price'

class BookThisLink extends PureComponent {
  children = priceRange => (
    <Fragment>
      <Price
        className="pc-ticket-button-price flex-columns items-center"
        free="Gratuit"
        value={priceRange}
      />
      <span className="pc-ticket-button-label">{'J’y vais !'}</span>
    </Fragment>
  )

  render() {
    const { destinationLink, isNotBookable, priceRange } = this.props

    return isNotBookable ? (
      <div className="flex-columns">{this.children(priceRange)}</div>
    ) : (
      <Link
        className="flex-columns"
        id="verso-booking-button"
        to={destinationLink}
      >
        {this.children(priceRange)}
      </Link>
    )
  }
}

BookThisLink.defaultProps = {
  isNotBookable: false,
}

BookThisLink.propTypes = {
  destinationLink: PropTypes.string.isRequired,
  isNotBookable: PropTypes.bool,
  priceRange: PropTypes.arrayOf(PropTypes.number.isRequired).isRequired,
}

export default BookThisLink
