import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { Fragment } from 'react'

import BookingsList from './BookingsList/BookingsList'
import Icon from '../../../layout/Icon/Icon'
import NoItems from '../../../layout/NoItems/NoItems'
import RelativeFooterContainer from '../../../layout/RelativeFooter/RelativeFooterContainer'

const MyBookingsLists = ({
  bookingsOfTheWeek,
  finishedAndUsedAndCancelledBookings,
  isEmpty,
  upComingBookings,
}) => (
  <Fragment>
    <main className={classnames('teaser-main', { 'teaser-no-teasers': isEmpty })}>
      {isEmpty && <NoItems sentence="Dès que vous aurez réservé une offre," />}

      {!isEmpty && bookingsOfTheWeek.length > 0 && (
        <section className="mb-section">
          <header className="mb-header">{'Cette semaine'}</header>
          <BookingsList bookings={bookingsOfTheWeek} />
        </section>
      )}

      {!isEmpty && (
        <section className="mb-section">
          <div className="mb-info-picto">
            <Icon
              alt="erreur"
              svg="picto-info"
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
          <header className="mb-header">{'À venir'}</header>
          <BookingsList bookings={upComingBookings} />
        </section>
      )}

      {!isEmpty && finishedAndUsedAndCancelledBookings.length > 0 && (
        <section className="mb-section">
          <header className="mb-header">{'Terminées'}</header>
          <BookingsList bookings={finishedAndUsedAndCancelledBookings} />
        </section>
      )}
    </main>
    <RelativeFooterContainer
      className="dotted-top-white"
      theme="purple"
    />
  </Fragment>
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
