import React, { PureComponent } from 'react'
import Main from '../../layout/Main'
import Titles from '../../layout/Titles/Titles'
import BookingsRecapTable from './BookingsRecapTable/BookingsRecapTable'
import PropTypes from 'prop-types'

class BookingsRecap extends PureComponent {
  constructor(props) {
    super(props)
    this.state = { bookingsRecap: [] }
  }

  componentDidMount() {
    const { requestGetAllBookingsRecap } = this.props
    requestGetAllBookingsRecap(this.handleSuccess)
  }

  handleSuccess = (state, action = {}) => {
    const { payload = {} } = action
    const { data } = payload
    this.setState({ bookingsRecap: data })
  }

  render() {
    const { bookingsRecap } = this.state
    return (
      <Main name="bookings-v2">
        <Titles title="Réservations V2" />
        <BookingsRecapTable bookingsRecap={bookingsRecap} />
      </Main>
    )
  }
}

BookingsRecap.propTypes = {
  requestGetAllBookingsRecap: PropTypes.func.isRequired,
}

export default BookingsRecap
