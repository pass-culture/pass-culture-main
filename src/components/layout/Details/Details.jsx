import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import { Route } from 'react-router-dom'

import BookingContainer from '../Booking/BookingContainer'
import RectoContainer from '../Recto/RectoContainer'
import VersoContainer from '../Verso/VersoContainer'

class Details extends PureComponent {
  renderBooking = route => (<BookingContainer
    extraClassName="with-header"
    {...route}
                            />)

  render() {
    const { areDetails, bookingPath } = this.props

    return (
      <Fragment>
        <Route
          path={bookingPath}
          render={this.renderBooking}
        />
        <VersoContainer
          areDetailsVisible={areDetails}
          extraClassName="with-header"
        />
        {areDetails && <RectoContainer
          areDetailsVisible
          extraClassName="with-header"
                       />}
      </Fragment>
    )
  }
}

Details.defaultProps = {
  areDetails: false,
}

Details.propTypes = {
  areDetails: PropTypes.bool,
  bookingPath: PropTypes.string.isRequired,
}

export default Details
