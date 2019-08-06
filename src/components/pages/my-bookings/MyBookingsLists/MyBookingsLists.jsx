import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { Fragment } from 'react'

import BookingsList from './BookingsList/BookingsList'
import NoItems from '../../../layout/NoItems/NoItems'
import RelativeFooterContainer from '../../../layout/RelativeFooter/RelativeFooterContainer'

const MyBookingsLists = ({ isEmpty, otherBookings, soonBookings }) => (
  <Fragment>
    <main className={classnames('teaser-main', { 'teaser-no-teasers': isEmpty })}>
      {isEmpty && <NoItems sentence="Dès que vous aurez réservé une offre," />}

      {!isEmpty && soonBookings.length > 0 && (
        <section className="mb-section">
          <header className="mb-header">{'C’est bientôt !'}</header>
          <BookingsList bookings={soonBookings} />
        </section>
      )}

      {!isEmpty && otherBookings.length > 0 && (
        <section className="mb-section">
          <header className="mb-header">{'Réservations'}</header>
          <BookingsList bookings={otherBookings} />
        </section>
      )}
    </main>
    <RelativeFooterContainer
      className="dotted-top-white"
      theme="purple"
    />
  </Fragment>
)

MyBookingsLists.propTypes = {
  isEmpty: PropTypes.bool.isRequired,
  otherBookings: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  soonBookings: PropTypes.arrayOf(PropTypes.shape()).isRequired,
}

export default MyBookingsLists
