import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import { Route, Switch } from 'react-router'

import { ApiError } from '../../layout/ErrorBoundaries/ApiError'
import HeaderContainer from '../../layout/Header/HeaderContainer'
import LoaderContainer from '../../layout/Loader/LoaderContainer'
import MyBookingDetailsContainer from './MyBookingDetails/MyBookingDetailsContainer'
import QrCodeContainer from './MyBookingsLists/BookingsList/QrCode/QrCodeContainer'
import MyBookingsListsContainer from './MyBookingsLists/MyBookingsListsContainer'

class MyBookings extends PureComponent {
  constructor(props) {
    super(props)

    this.state = {
      isLoading: true,
    }
  }

  componentDidMount() {
    const { requestGetBookings } = this.props

    requestGetBookings(this.handleFail, this.handleSuccess)
  }

  handleFail = (state, action) => {
    this.setState(() => {
      throw new ApiError(action.payload.status)
    })
  }

  handleSuccess = () => {
    this.setState({
      isLoading: false,
    })
  }

  render() {
    const { bookings, isQrCodeFeatureDisabled, match } = this.props
    const { isLoading } = this.state
    const hasNoBookings = bookings.length === 0

    return (
      <Fragment>
        {isLoading && <LoaderContainer />}

        {!isLoading && (
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
        )}
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
