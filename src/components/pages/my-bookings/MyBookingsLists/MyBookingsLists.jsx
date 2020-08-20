import PropTypes from 'prop-types'
import React from 'react'

import BookingsList from './BookingsList/BookingsList'
import Icon from '../../../layout/Icon/Icon'
import NoItems from '../../../layout/NoItems/NoItems'

const MyBookingsLists = ({
  bookingsOfTheWeek,
  finishedAndUsedAndCancelledBookings,
  isEmpty,
  isHomepageDisabled,
  upComingBookings,
}) => (
  <main className="teaser-page">
    <h1 className="teaser-main-title">
      {'Réservations'}
    </h1>

    {isEmpty && (
      <NoItems
        isHomepageDisabled={isHomepageDisabled}
        sentence="Dès que tu auras réservé une offre, tu la retrouveras ici."
      />
    )}

    {!isEmpty && bookingsOfTheWeek.length > 0 && (
      <section className="mb-section">
        <h2 className="mb-subtitle">
          {'Cette semaine'}
        </h2>
        <BookingsList bookings={bookingsOfTheWeek} />
      </section>
    )}

    {!isEmpty && (
      <section className="mb-section">
        <div className="mb-info-picto">
          <Icon svg="ico-info-white" />
        </div>
        <p className="mb-infos">
          {
            'Le code de réservation à 6 caractères est ta preuve d’achat. Ne communique ce code qu’au moment du retrait de ta commande.'
          }
        </p>
      </section>
    )}

    {!isEmpty && upComingBookings.length > 0 && (
      <section className="mb-section">
        <h2 className="mb-subtitle">
          {'À venir'}
        </h2>
        <BookingsList bookings={upComingBookings} />
      </section>
    )}

    {!isEmpty && finishedAndUsedAndCancelledBookings.length > 0 && (
      <section className="mb-section">
        <h2 className="mb-subtitle">
          {'Terminées'}
        </h2>
        <BookingsList
          bookings={finishedAndUsedAndCancelledBookings}
          shouldDisplayToken={false}
        />
      </section>
    )}
  </main>
)

MyBookingsLists.defaultProps = {
  isEmpty: true,
}

MyBookingsLists.propTypes = {
  bookingsOfTheWeek: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  finishedAndUsedAndCancelledBookings: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  isEmpty: PropTypes.bool,
  isHomepageDisabled: PropTypes.bool.isRequired,
  upComingBookings: PropTypes.arrayOf(PropTypes.shape()).isRequired,
}

export default MyBookingsLists
