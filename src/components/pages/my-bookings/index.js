import get from 'lodash.get'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { bindActionCreators, compose } from 'redux'
import { requestData } from 'redux-saga-data'

import MyBookingContainer from './MyBookingContainer'
import NoBookingView from './NoBookingView'
import { mapStateToProps } from './connect'
import { withRequiredLogin } from '../../hocs'
import LoaderContainer from '../../layout/Loader/LoaderContainer'
import PageHeader from '../../layout/Header/PageHeader'
import { toggleMainMenu } from '../../../reducers/menu'
import NavigationFooter from '../../layout/NavigationFooter'
import { ROOT_PATH } from '../../../utils/config'

const renderBookingList = items => (
  <ul className="bookings">
    {items.map(booking => {
      const key = booking.id
      return <MyBookingContainer key={key} booking={booking} />
    })}
  </ul>
)

export class RawMyBookingsPage extends Component {
  constructor(props) {
    super(props)
    const { dispatch } = props
    const actions = { requestData, toggleMainMenu }
    this.actions = bindActionCreators(actions, dispatch)
    this.state = { hasError: false, isEmpty: false, isLoading: true }
  }

  componentWillMount = () => {
    this.actions.requestData({
      apiPath: '/bookings',
      handleFail: this.handleRequestFail,
      handleSuccess: this.handleRequestSuccess,
      stateKey: 'bookings',
    })
  }

  handleRequestFail = () => {
    // ERREUR DE CHARGEMENT
    this.setState({ hasError: true, isLoading: true })
  }

  handleRequestSuccess = (state, action) => {
    const data = get(action, 'payload.data')
    const len = data.length
    const isEmpty = !(len && len > 0)
    this.setState({ isEmpty, isLoading: false })
  }

  render() {
    const { soonBookings, otherBookings } = this.props
    const { isEmpty, isLoading, hasError } = this.state
    const soonBookingsLength = soonBookings.length
    const otherBookingsLength = otherBookings.length
    const hasNoBooking = soonBookingsLength === 0 && otherBookingsLength === 0
    const backgroundImage = `url('${ROOT_PATH}/mosaic-k.png')`
    return (
      <div
        id="bookings-page"
        className="page is-relative flex-rows with-header"
      >
        {!isLoading && (
          <React.Fragment>
            <PageHeader title="Mes réservations" />
            <main
              role="main"
              className="pc-main pc-gradient flex-rows flex-start is-clipped"
            >
              <div className="pc-scroll-container" style={{ backgroundImage }}>
                {soonBookingsLength > 0 && (
                  <div className="px12 mt36">
                    <h4 className="mb16 fs19 is-uppercase is-white-text">
                      <i>C&apos;est bientôt !</i>
                    </h4>
                    {renderBookingList(soonBookings)}
                  </div>
                )}
                {otherBookingsLength > 0 && (
                  <div className="px12 my36">
                    <h4 className="mb16 fs19 is-uppercase is-white-text">
                      <i>Réservations</i>
                    </h4>
                    {renderBookingList(otherBookings)}
                  </div>
                )}
                {(isEmpty || hasNoBooking) && <NoBookingView />}
              </div>
            </main>
            <NavigationFooter theme="purple" className="dotted-top-white" />
          </React.Fragment>
        )}
        {!isEmpty && (
          <LoaderContainer
            isEmpty={isEmpty}
            hasError={hasError}
            isLoading={isLoading}
          />
        )}
      </div>
    )
  }
}

RawMyBookingsPage.propTypes = {
  dispatch: PropTypes.func.isRequired,
  otherBookings: PropTypes.array.isRequired,
  soonBookings: PropTypes.array.isRequired,
}

export default compose(
  withRequiredLogin,
  connect(mapStateToProps)
)(RawMyBookingsPage)
