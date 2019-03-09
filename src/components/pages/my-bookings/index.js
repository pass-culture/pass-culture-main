/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { bindActionCreators, compose } from 'redux'
import { assignData, requestData } from 'redux-saga-data'

import MyBookingItem from './MyBookingItem'
import NoBookingView from './NoBookingView'
import { mapStateToProps } from './connect'
import { withRedirectToSigninWhenNotAuthenticated } from '../../hocs'
import Loader from '../../layout/Loader'
import PageHeader from '../../layout/PageHeader'
import { toggleMainMenu } from '../../../reducers/menu'
import NavigationFooter from '../../layout/NavigationFooter'
import { ROOT_PATH } from '../../../utils/config'
import { bookingNormalizer } from '../../../utils/normalizers'

const renderBookingList = items => (
  <ul className="bookings">
    {items.map(booking => {
      const key = booking.id
      return <MyBookingItem key={key} booking={booking} />
    })}
  </ul>
)

class MyBookingsPage extends Component {
  constructor(props) {
    super(props)
    const { dispatch } = props
    const actions = { requestData, toggleMainMenu }
    this.actions = bindActionCreators(actions, dispatch)
    this.state = { haserror: false, isempty: false, isloading: true }
  }

  componentWillMount = () => {
    this.actions.requestData({
      apiPath: '/bookings',
      handleFail: this.handleRequestFail,
      handleSuccess: this.handleRequestSuccess,
      normalizer: bookingNormalizer,
    })
  }

  componentWillUnmount() {
    const { dispatch } = this.props
    dispatch(assignData({ recommendations: [] }))
  }

  handleRequestFail = () => {
    // ERREUR DE CHARGEMENT
    this.setState({ haserror: true, isloading: true })
  }

  handleRequestSuccess = (state, action) => {
    const {
      payload: { data },
    } = action
    const len = data.length
    const isempty = !(len && len > 0)
    this.setState({ isempty, isloading: false })
  }

  render() {
    const { soonBookings, otherBookings } = this.props
    const { isempty, isloading, haserror } = this.state
    // NOTE -> perfs: calculate length once
    const soonBookingsLength = soonBookings.length
    const otherBookingsLength = otherBookings.length
    const hasNoBooking = soonBookingsLength === 0 && otherBookingsLength === 0
    const backgroundImage = `url('${ROOT_PATH}/mosaic-k.png')`
    return (
      <div id="bookings-page" className="page is-relative flex-rows">
        {!isloading && (
          <React.Fragment>
            <PageHeader
              useClose
              title="Mes réservations"
              className="dotted-bottom-white"
            />
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
                {/*
                FIXME: calcul qui n'a pas de sens sur deux choix
                - si aucune reservations API
                - si aucune reservations dans les deja charges
              */}
                {(isempty || hasNoBooking) && <NoBookingView />}
              </div>
            </main>
            <NavigationFooter theme="purple" className="dotted-top-white" />
          </React.Fragment>
        )}
        {!isempty && (
          <Loader isempty={isempty} haserror={haserror} isloading={isloading} />
        )}
      </div>
    )
  }
}

MyBookingsPage.propTypes = {
  dispatch: PropTypes.func.isRequired,
  otherBookings: PropTypes.array.isRequired,
  soonBookings: PropTypes.array.isRequired,
}

export default compose(
  withRedirectToSigninWhenNotAuthenticated,
  connect(mapStateToProps)
)(MyBookingsPage)
