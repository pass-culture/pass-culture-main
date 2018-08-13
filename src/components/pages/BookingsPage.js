import PropTypes from 'prop-types'
import { requestData } from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { Link } from 'react-router-dom'

import BookingItem from '../BookingItem'
import Main from '../layout/Main'
import Footer from '../layout/Footer'
import otherBookingsSelector from '../../selectors/otherBookings'
import soonBookingsSelector from '../../selectors/soonBookings'
import { bookingNormalizer } from '../../utils/normalizers'

const renderPageHeader = () => (
  <header>
    <h1>
      {'Mes réservations'}
    </h1>
  </header>
)

const renderPageFooter = () => {
  const footerProps = { borderTop: true }
  return <Footer {...footerProps} />
}

class BookingsPage extends Component {
  handleDataRequest = (handleSuccess, handleFail) => {
    const { dispatchRequestData } = this.props
    dispatchRequestData('GET', 'bookings', {
      handleFail,
      handleSuccess,
      normalizer: bookingNormalizer,
    })
  }

  render() {
    const { soonBookings, otherBookings } = this.props
    return (
      <Main
        backButton
        header={renderPageHeader}
        handleDataRequest={this.handleDataRequest}
        name="bookings"
        footer={renderPageFooter}
        redBg
      >
        {soonBookings.length > 0 && (
          <div>
            <h4>
              {"C'est bientôt !"}
            </h4>
            <ul className="bookings">
              {soonBookings.map(booking => (
                <BookingItem key={booking.id} booking={booking} />
              ))}
            </ul>
          </div>
        )}
        {otherBookings.length > 0 && (
          <div>
            <h4>
Réservations
            </h4>
            <ul className="bookings">
              {otherBookings.map(booking => (
                <BookingItem key={booking.id} booking={booking} />
              ))}
            </ul>
          </div>
        )}
        {soonBookings.length === 0 &&
          otherBookings.length === 0 && (
            <div>
              <p className="nothing">
Pas encore de réservation.
              </p>
              <p className="nothing">
                <Link to="/decouverte" className="button is-primary">
                  Allez-y !
                </Link>
              </p>
            </div>
          )}
      </Main>
    )
  }
}

BookingsPage.propTypes = {
  dispatchRequestData: PropTypes.func.isRequired,
  otherBookings: PropTypes.array.isRequired,
  soonBookings: PropTypes.array.isRequired,
}

export default compose(
  connect(
    state => ({
      otherBookings: otherBookingsSelector(state),
      soonBookings: soonBookingsSelector(state),
    }),
    { dispatchRequestData: requestData }
  )
)(BookingsPage)
