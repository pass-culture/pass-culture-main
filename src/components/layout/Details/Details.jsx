import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import { Route } from 'react-router-dom'

import BookingContainer from '../../pages/Booking/BookingContainer'
import BookingCancellationContainer from '../../pages/BookingCancellation/BookingCancellationContainer'
import isDetailsView from '../../../helpers/isDetailsView'

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
    const { isConfirmingCancelling } = this.props

    return isConfirmingCancelling
      ? this.renderBookingCancellation(route)
      : this.renderBooking(route)
  }

  renderBookingCancellation = route => {
    return (<BookingCancellationContainer
      extraClassName="with-header"
      {...route}
            />)
  }

  renderBooking = route => (<BookingContainer
    extraClassName="with-header"
    {...route}
                            />)

  render() {
    const { bookingPath } = this.props
    const { isDetailsView } = this.state

    return (
      <Fragment>
        <Route
          path={bookingPath}
          render={this.renderBookingOrCancellation}
        />
        <VersoContainer
          areDetailsVisible={isDetailsView}
          extraClassName="with-header"
        />
        {isDetailsView && <RectoContainer areDetailsVisible />}
      </Fragment>
    )
  }
}

Details.defaultProps = {
  isConfirmingCancelling: false,
}

Details.propTypes = {
  bookingPath: PropTypes.string.isRequired,
  isConfirmingCancelling: PropTypes.bool,
  match: PropTypes.shape({
    params: PropTypes.shape({
      details: PropTypes.string,
    }),
  }).isRequired,
}

export default Details
