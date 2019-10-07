import PropTypes from 'prop-types'
import React, { Component } from 'react'

import MyBookingsListsContainer from './MyBookingsLists/MyBookingsListsContainer'
import MyBookingDetailsContainer from './MyBookingDetails/MyBookingDetailsContainer'
import HeaderContainer from '../../layout/Header/HeaderContainer'
import LoaderContainer from '../../layout/Loader/LoaderContainer'

class MyBookings extends Component {
  constructor(props) {
    super(props)

    this.state = {
      hasError: false,
      isLoading: true,
    }
  }

  componentDidMount = () => {
    const { requestGetBookings } = this.props
    requestGetBookings(this.handleFail, this.handleSuccess)
  }

  handleFail = () => {
    this.setState({
      hasError: true,
      isLoading: true,
    })
  }

  handleSuccess = () => {
    this.setState({
      isLoading: false,
    })
  }

  render() {
    const { bookings } = this.props
    const { hasError, isLoading } = this.state
    const isEmpty = bookings.length === 0

    if (isLoading) {
      return (<LoaderContainer
        hasError={hasError}
        isLoading={isLoading}
              />)
    }

    return (
      <div className="teaser-list">
        <HeaderContainer
          shouldBackFromDetails
          title="Mes réservations"
        />
        <MyBookingsListsContainer isEmpty={isEmpty} />
        <MyBookingDetailsContainer bookingPath="/reservations/:details(details|transition)/:bookingId([A-Z0-9]+)/:booking(reservation)/:cancellation(annulation)?/:confirmation(confirmation)?" />
      </div>
    )
  }
}

MyBookings.propTypes = {
  bookings: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  location: PropTypes.shape({
    pathname: PropTypes.string.isRequired,
    search: PropTypes.string.isRequired,
  }).isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      details: PropTypes.string,
    }).isRequired,
  }).isRequired,
  requestGetBookings: PropTypes.func.isRequired,
}

export default MyBookings
