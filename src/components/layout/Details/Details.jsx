import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import { Route } from 'react-router-dom'

import BookingContainer from '../Booking/BookingContainer'
import VersoContainer from '../Verso/VersoContainer'
import getAreDetailsVisible from '../../../helpers/getAreDetailsVisible'

class Details extends PureComponent {
  renderBooking = route => {
    return (<BookingContainer
      extraClassName="with-header"
      {...route}
            />)
  }

  render() {
    const { bookingPath, match } = this.props
    const showDetails = getAreDetailsVisible(match)
    return (
      <Fragment>
        <Route
          path={bookingPath}
          render={this.renderBooking}
        />
        <VersoContainer
          areDetailsVisible={showDetails}
          extraClassName="with-header"
        />
      </Fragment>
    )
  }
}

Details.propTypes = {
  bookingPath: PropTypes.string.isRequired,
  hasReceivedData: PropTypes.bool.isRequired,
  history: PropTypes.shape({
    push: PropTypes.func.isRequired,
  }).isRequired,
  location: PropTypes.shape({
    pathname: PropTypes.string,
    search: PropTypes.string,
  }).isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      details: PropTypes.string,
    }).isRequired,
  }).isRequired,
  needsToRequestGetData: PropTypes.bool.isRequired,
  requestGetData: PropTypes.func.isRequired,
}

export default Details
