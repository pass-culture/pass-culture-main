import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { Link } from 'react-router-dom'

import BookingItem from '../components/BookingItem'
import withLogin from '../hocs/withLogin'
import { requestData } from '../reducers/data'
import MenuButton from '../components/layout/MenuButton'
import selectBookingsByTime from '../selectors/bookingsByTime'

class BookingsPage extends Component {

  componentDidMount() {
    this.handleRequestBookings()
  }

  handleRequestBookings = () => {
    this.props.requestData('GET', 'bookings', { local: true })
  }

  render() {
    const {
      soonBookings,
      otherBookings,
    } = this.props.bookingsByTime;
    return (
      <div className='page bookings-page'>
        <header>Mes réservations</header>
        <div className='content'>
          { soonBookings.length > 0 && (
            <div>
              <h4>C'est bientôt !</h4>
              <ul className='bookings'>
                {soonBookings.map((b, index) => <BookingItem key={index} {...b} />)}
              </ul>
            </div>
          )}
          {otherBookings.length > 0 && (
            <div>
              <h4>Réservations</h4>
              <ul className='bookings'>
                {otherBookings.map((b, index) => <BookingItem key={index} {...b} />)}
              </ul>
            </div>
          )}
          { soonBookings.length === 0 && otherBookings.length === 0 && (
            <div>
              <p className='nothing'>
                Pas encore de réservation.
              </p>
              <p className='nothing'>
                <Link to='/decouverte' className='button button--primary'>Allez-y !</Link>
              </p>
            </div>
          )}
        </div>
        <MenuButton borderTop />
      </div>
    )
  }
}

export default compose(
  withLogin({ isRequired: true }),
  connect(
    state => ({
      bookingsByTime: selectBookingsByTime(state),
    }),
    { requestData }
  )
)(BookingsPage)
