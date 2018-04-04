import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import withLogin from '../hocs/withLogin'
import { requestData } from '../reducers/data'

class BookingsPage extends Component {
  handleRequestBookings = () => {
    this.props.requestData('GET', 'bookings', { local: true })
  }
  componentDidMount () {
    this.handleRequestBookings()
  }
  render () {
    const { bookings } = this.props
    return (
      <main className='page'>
        {
          bookings && bookings.map((booking, index) => (
            <div key={index}>
              { booking.token }
            </div>
          ))
        }
      </main>
    )
  }
}

export default compose(
  withLogin({ isRequired: true }),
  connect(
    state => ({
      bookings: state.data.bookings
    }),
    { requestData }
  )
)(BookingsPage)
