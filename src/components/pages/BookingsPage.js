/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import { requestData } from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'
import { Link } from 'react-router-dom'

import BookingItem from '../BookingItem'
import Main from '../layout/Main'
import Footer from '../layout/Footer'
import {
  selectSoonBookings,
  selectOtherBookings,
} from '../../selectors/selectBookings'
import { bookingNormalizer } from '../../utils/normalizers'

const renderPageHeader = () => (
  <header>
    <h1>Mes réservations</h1>
  </header>
)

const renderPageFooter = () => {
  const footerProps = { borderTop: true }
  return <Footer {...footerProps} />
}

const renderNoBookingSection = () => (
  <div>
    <p className="nothing">Pas encore de réservation.</p>
    <p className="nothing">
      <Link to="/decouverte" className="button is-primary">
        Allez-y !
      </Link>
    </p>
  </div>
)

const renderBookingList = items => (
  <ul className="bookings">
    {items.map(booking => (
      <BookingItem key={booking.id} booking={booking} />
    ))}
  </ul>
)

class BookingsPage extends Component {
  constructor(props) {
    super(props)
    const { dispatch } = props
    const actions = { requestData }
    this.actions = bindActionCreators(actions, dispatch)
  }

  handleDataRequest = (handleSuccess, handleFail) => {
    this.actions.requestData('GET', 'bookings', {
      handleFail,
      handleSuccess,
      normalizer: bookingNormalizer,
    })
  }

  render() {
    const { soonBookings, otherBookings } = this.props
    // NOTE -> perfs: calculate length once
    const soonBookingsLength = soonBookings.length
    const otherBookingsLength = otherBookings.length
    const hasNoBooking = soonBookingsLength === 0 && otherBookingsLength === 0
    return (
      <Main
        backButton
        header={renderPageHeader}
        handleDataRequest={this.handleDataRequest}
        name="bookings"
        footer={renderPageFooter}
        redBg
      >
        {soonBookingsLength > 0 && (
          <div>
            <h4>C&apos;est bientôt !</h4>
            {renderBookingList(soonBookings)}
          </div>
        )}
        {otherBookingsLength > 0 && (
          <div>
            <h4>Réservations</h4>
            {renderBookingList(otherBookings)}
          </div>
        )}
        {hasNoBooking && renderNoBookingSection()}
      </Main>
    )
  }
}

BookingsPage.propTypes = {
  dispatch: PropTypes.func.isRequired,
  otherBookings: PropTypes.array.isRequired,
  soonBookings: PropTypes.array.isRequired,
}

const mapStateToProps = state => {
  const otherBookings = selectOtherBookings(state)
  const soonBookings = selectSoonBookings(state)
  return { otherBookings, soonBookings }
}

export default connect(mapStateToProps)(BookingsPage)
