import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'

import MyBookingsListsContainer from './MyBookingsLists/MyBookingsListsContainer'
import MyBookingDetailsContainer from './MyBookingDetails/MyBookingDetailsContainer'
import HeaderContainer from '../../layout/Header/HeaderContainer'
import LoaderContainer from '../../layout/Loader/LoaderContainer'
import { Route, Switch } from 'react-router'
import QrCodeContainer from './MyBookingsLists/BookingsList/QrCode/QrCodeContainer'

class MyBookings extends PureComponent {
  constructor(props) {
    super(props)

    this.state = {
      hasError: false,
      isLoading: true,
    }
  }

  componentDidMount() {
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
    const { bookings, isQrCodeFeatureDisabled, match } = this.props
    const { hasError, isLoading } = this.state
    const hasNoBookings = bookings.length === 0

    if (isLoading) {
      return (<LoaderContainer
        hasError={hasError}
        isLoading={isLoading}
              />)
    }

    return (
      <Fragment>
        <MyBookingsListsContainer isEmpty={hasNoBookings} />

        <Switch>
          <Route
            exact
            path={`${match.path}/:details(details|transition)/:bookingId([A-Z0-9]+)/:booking(reservation)?/:cancellation(annulation)?/:confirmation(confirmation)?`}
            sensitive
          >
            <div className="offer-details">
              <HeaderContainer
                shouldBackFromDetails
                title="Réservations"
              />
              <MyBookingDetailsContainer
                bookingPath={`${match.path}/:details(details|transition)/:bookingId([A-Z0-9]+)/:booking(reservation)/:cancellation(annulation)?/:confirmation(confirmation)?`}
              />
            </div>
          </Route>
          <Route
            exact
            path={`${match.path}/:details(details)/:bookingId([A-Z0-9]+)/:qrcode(qrcode)`}
            sensitive
          >
            {!isQrCodeFeatureDisabled && (
              <div className="offer-details">
                <HeaderContainer
                  backTo={match.path}
                  title="Réservations"
                />
                <QrCodeContainer />
              </div>
            )}
          </Route>
        </Switch>
      </Fragment>
    )
  }
}

MyBookings.propTypes = {
  bookings: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  isQrCodeFeatureDisabled: PropTypes.bool.isRequired,
  location: PropTypes.shape({
    pathname: PropTypes.string.isRequired,
    search: PropTypes.string.isRequired,
  }).isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      details: PropTypes.string,
    }).isRequired,
    path: PropTypes.string.isRequired,
  }).isRequired,
  requestGetBookings: PropTypes.func.isRequired,
}

export default MyBookings
