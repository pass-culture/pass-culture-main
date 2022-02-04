import PropTypes from 'prop-types'
import React from 'react'

import { pluralize } from '../../../../../utils/pluralize'

const Header = ({ bookingsRecapFiltered, isLoading }) => {
  if (isLoading) {
    return (
      <div className="bookings-header-loading">
        Chargement des réservations...
      </div>
    )
  } else {
    return (
      <div className="bookings-header">
        <span className="bookings-header-number">
          {pluralize(bookingsRecapFiltered.length, 'réservation')}
        </span>
      </div>
    )
  }
}

Header.propTypes = {
  bookingsRecapFiltered: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  isLoading: PropTypes.bool.isRequired,
}

export default Header
