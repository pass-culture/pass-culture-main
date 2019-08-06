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
      isEmpty: false,
      isLoading: true,
    }
  }

  componentDidMount = () => {
    const { requestGetBookings } = this.props
    requestGetBookings(this.handleFail, this.handleSuccess)
  }

  componentDidUpdate = prevProps => {
    const { validBookings } = this.props
    const { isEmpty } = this.state
    if (validBookings && validBookings !== prevProps.validBookings) {
      if (validBookings.length === 0) {
        this.handleSetIsEmpty(true)
      } else if (!isEmpty) {
        this.handleSetIsEmpty(false)
      }
    }
  }

  componentWillUnmount() {
    const { resetPageData } = this.props
    resetPageData()
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

  handleSetIsEmpty = isEmpty => {
    this.setState({ isEmpty })
  }

  render() {
    const { hasError, isEmpty, isLoading } = this.state

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
        <MyBookingDetailsContainer bookingPath="/reservations/:details(details|transition)/:bookingId([A-Z0-9]+)/:bookings(reservations)/:cancellation(annulation)?/:confirmation(confirmation)?" />
      </div>
    )
  }
}

MyBookings.propTypes = {
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
  resetPageData: PropTypes.func.isRequired,
  validBookings: PropTypes.arrayOf(PropTypes.shape()).isRequired,
}

export default MyBookings
