import PropTypes from 'prop-types'
import React from 'react'

import BookingsList from './BookingsList/BookingsList'
import Icon from '../../../layout/Icon/Icon'
import NoItems from '../../../layout/NoItems/NoItems'

const MyBookingsLists = ({
  bookingsOfTheWeek,
  finishedAndUsedAndCancelledBookings,
  isEmpty,
  upComingBookings,
}) => (
  <main className={`teaser-page ${isEmpty ? 'teaser-no-teasers' : ''}`}>
    <h1 className="teaser-main-title">
      {'Réservations'}
    </h1>

    {isEmpty && (
      <NoItems sentence="Dès que vous aurez réservé une offre, vous la retrouverez ici." />
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
          <Icon
            alt="erreur"
            svg="ico-info-white"
          />
        </div>
        <p className="mb-infos">
          {
            'Le code de réservation à 6 caractères est votre preuve d’achat. Ne communiquez ce code qu’au moment du retrait de votre commande.'
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
  upComingBookings: PropTypes.arrayOf(PropTypes.shape()).isRequired,
}

export default MyBookingsLists
