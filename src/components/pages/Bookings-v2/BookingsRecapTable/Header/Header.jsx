import React from 'react'
import PropTypes from 'prop-types'
import { pluralizeWord } from './utils/pluralizeWord'

const Header = ({ isLoading, nbBookings }) => (
  <div className="bookings-header">
    {isLoading ? (
      <span>
        {'Chargement des réservations...'}
      </span>
    ) : (
      <span>
        {nbBookings > 0 && `${nbBookings} ${pluralizeWord(nbBookings, 'réservation')}`}
      </span>
    )}
  </div>
)

Header.propTypes = {
  isLoading: PropTypes.bool.isRequired,
  nbBookings: PropTypes.number.isRequired,
}

export default Header
