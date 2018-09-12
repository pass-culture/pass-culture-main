/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import { requestData, withLogin } from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { bindActionCreators, compose } from 'redux'
import { Link } from 'react-router-dom'
import get from 'lodash.get'
import { Scrollbars } from 'react-custom-scrollbars'

import BookingItem from '../layout/BookingItem'
import {
  selectSoonBookings,
  selectOtherBookings,
  selectRecommendations,
} from '../../selectors'
import Loader from '../layout/Loader'
import PageHeader from '../layout/PageHeader'
import { toggleMainMenu } from '../../reducers/menu'
import NavigationFooter from '../layout/NavigationFooter'
import { bookingNormalizer } from '../../utils/normalizers'

const renderNoBookingSection = () => (
  <div className="has-text-centered">
    <p className="mt20">
      <b>Pas encore de réservation.</b>
    </p>
    <p className="mt20">
      <Link to="/decouverte" className="button is-primary">
        Allez-y !
      </Link>
    </p>
  </div>
)

const renderBookingList = items => (
  <ul className="bookings">
    {items.map(booking => {
      const key = booking.id
      return <BookingItem key={key} booking={booking} />
    })}
  </ul>
)

class BookingsPage extends Component {
  constructor(props) {
    super(props)
    const { dispatch } = props
    const actions = { requestData, toggleMainMenu }
    this.actions = bindActionCreators(actions, dispatch)
    this.state = { haserror: false, isempty: false, isloading: true }
  }

  componentWillMount = () => {
    const serviceURI = 'bookings'
    this.actions.requestData('GET', serviceURI, {
      handleFail: this.handleRequestFail,
      handleSuccess: this.handleRequestSuccess,
      normalizer: bookingNormalizer,
    })
  }

  handleRequestFail = () => {
    // ERREUR DE CHARGEMENT
    this.setState({ haserror: true, isloading: true })
  }

  handleRequestSuccess = (state, action) => {
    const len = get(action, 'data.length')
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
    return (
      <div id="bookings-page" className="page is-relative flex-rows">
        {!isloading && (
          <React.Fragment>
            <PageHeader
              title="Mes réservations"
              className="dotted-bottom-white"
            />
            <main
              role="main"
              className="pc-main pc-gradient padded flex-rows flex-start"
            >
              <Scrollbars>
                {soonBookingsLength > 0 && (
                  <div>
                    <h4 className="mb16 fs19 is-uppercase is-white-text">
                      <i>C&apos;est bientôt !</i>
                    </h4>
                    {renderBookingList(soonBookings)}
                  </div>
                )}
                {otherBookingsLength > 0 && (
                  <div>
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
                {(isempty || hasNoBooking) && renderNoBookingSection()}
              </Scrollbars>
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

BookingsPage.propTypes = {
  dispatch: PropTypes.func.isRequired,
  otherBookings: PropTypes.array.isRequired,
  soonBookings: PropTypes.array.isRequired,
}

const mapStateToProps = state => {
  const recommendations = selectRecommendations(state)
  const otherBookings = selectOtherBookings(state)
  const soonBookings = selectSoonBookings(state)
  return { otherBookings, recommendations, soonBookings }
}

export default compose(
  withLogin({ failRedirect: '/connexion' }),
  connect(mapStateToProps)
)(BookingsPage)
