import React from 'react'

import { pluralize } from 'utils/pluralize'

export interface HeaderProps {
  bookingsRecapFilteredLength: number
  isLoading: boolean
}

const Header = ({ bookingsRecapFilteredLength, isLoading }: HeaderProps) => {
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
          {pluralize(bookingsRecapFilteredLength, 'réservation')}
        </span>
      </div>
    )
  }
}

export default Header
