import React from 'react'
import PropTypes from 'prop-types'
import { pluralizeWord } from './utils/pluralizeWord'
import Spinner from '../../../../layout/Spinner'
import Icon from '../../../../layout/Icon'

const Header = ({isLoading, nbBookings}) => (
  <div className="bookings-header">
    {isLoading ? (
      <span>
        Chargement en cours ...
      </span>
    ) : (
      <span>
        {nbBookings === 0 ?
          'Aucune réservation'
          : `${nbBookings} ${pluralizeWord(nbBookings, 'réservation')
        }`}
      </span>
    )}
  </div>
)

Header.defaultProps = {
  nbBookings: 0
}

Header.propTypes = {
  nbBookings: PropTypes.number
}

export default Header
