import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import { Route } from 'react-router-dom'

import isDetailsView from '../../../utils/isDetailsView'
import BookingContainer from '../../layout/Booking/BookingContainer'
import BookingCancellationContainer from '../../layout/BookingCancellation/BookingCancellationContainer'
import RectoContainer from '../Recto/RectoContainer'
import VersoContainer from '../Verso/VersoContainer'

class Details extends PureComponent {
  constructor(props) {
    super(props)

    this.state = {
      isDetailsView: false,
    }
  }

  componentDidMount() {
    this.handleSetIsDetailsView()
    const { getOfferById, match } = this.props
    const { params } = match
    const { offerId } = params
    getOfferById(offerId)
  }

  componentDidUpdate() {
    this.handleSetIsDetailsView()
  }

  handleSetIsDetailsView = () => {
    const { match } = this.props
    this.setState({
      isDetailsView: isDetailsView(match),
    })
  }

  renderBookingOrCancellation = route => {
    const { cancelView } = this.props

    return cancelView ? this.renderBookingCancellation(route) : this.renderBooking(route)
  }

  renderBookingCancellation = route => {
    const { withHeader } = this.props
    return (
      <BookingCancellationContainer
        extraClassName={`${withHeader ? 'with-header' : ''}`}
        {...route}
      />
    )
  }

  renderBooking = route => {
    const { withHeader } = this.props
    return (
      <BookingContainer
        extraClassName={`${withHeader ? 'with-header' : ''}`}
        {...route}
      />
    )
  }

  render() {
    const { bookingPath, withHeader } = this.props
    const { isDetailsView } = this.state

    return (
      <Fragment>
        <Route
          path={bookingPath}
          render={this.renderBookingOrCancellation}
          sensitive
        />
        <VersoContainer
          areDetailsVisible={isDetailsView}
          extraClassName={`${withHeader ? 'with-header' : ''}`}
        />
        {isDetailsView && <RectoContainer areDetailsVisible />}
      </Fragment>
    )
  }
}

Details.defaultProps = {
  bookingPath: '',
  cancelView: false,
  withHeader: true,
}

Details.propTypes = {
  bookingPath: PropTypes.string,
  cancelView: PropTypes.bool,
  getOfferById: PropTypes.func.isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      details: PropTypes.string,
      offerId: PropTypes.string,
    }),
  }).isRequired,
  withHeader: PropTypes.bool,
}

export default Details
