import React from 'react'
import PropTypes from 'prop-types'
import { pluralizeWord } from './utils/pluralizeWord'

const Header = ({nbBookings}) => (
  <div className="bookings-header">
    <span>
      {nbBookings === 0 ?
        'Aucune réservation'
        : `${nbBookings} ${pluralizeWord(nbBookings, 'réservation')
      }`}
    </span>
  </div>
)

Header.defaultProps = {
  nbBookings: 0
}

Header.propTypes = {
  nbBookings: PropTypes.number
}

export default Header
