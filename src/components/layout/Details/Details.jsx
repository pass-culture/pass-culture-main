import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import { Route } from 'react-router-dom'

import BookingContainer from '../Booking/BookingContainer'
import isDetailsView from '../../../helpers/isDetailsView'
import RectoContainer from '../Recto/RectoContainer'
import VersoContainer from '../Verso/VersoContainer'

class Details extends PureComponent {
  constructor() {
    super()

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
          render={this.renderBooking}
        />
        <VersoContainer
          areDetailsVisible={isDetailsView}
          extraClassName="with-header"
        />
        {isDetailsView && <RectoContainer
          areDetailsVisible
          extraClassName="with-header"
                          />}
      </Fragment>
    )
  }
}

Details.propTypes = {
  bookingPath: PropTypes.string.isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      details: PropTypes.string,
    }),
  }).isRequired,
}

export default Details
