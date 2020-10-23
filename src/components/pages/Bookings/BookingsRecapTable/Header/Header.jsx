import PropTypes from 'prop-types'
import React from 'react'
import { CSVLink } from 'react-csv'

import Icon from 'components/layout/Icon'

import { pluralize } from '../../../../../utils/pluralize'
import generateBookingsCsvFile from '../utils/generateBookingsCsvFile'

const Header = ({ bookingsRecapFiltered, isLoading }) => {
  if (isLoading) {
    return (
      <div className="bookings-header-loading">
        {'Chargement des réservations...'}
      </div>
    )
  } else {
    return (
      <div className="bookings-header">
        <span className="bookings-header-number">
          {pluralize(bookingsRecapFiltered.length, 'réservation')}
        </span>
        <span className="bookings-header-csv-download">
          <CSVLink
            data={generateBookingsCsvFile(bookingsRecapFiltered)}
            filename="Réservations Pass Culture.csv"
            separator=";"
          >
            <Icon
              alt="Télécharger le CSV"
              svg="ico-download"
            />
            {'Télécharger le CSV'}
          </CSVLink>
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
