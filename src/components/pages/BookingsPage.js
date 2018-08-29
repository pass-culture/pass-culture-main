/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import { requestData, withLogin } from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { bindActionCreators, compose } from 'redux'
import { Link } from 'react-router-dom'
import get from 'lodash.get'

import BookingItem from '../BookingItem'
import Main from '../layout/Main'
import Footer from '../layout/Footer'
import {
  selectSoonBookings,
  selectOtherBookings,
  selectRecommendations,
} from '../../selectors'
import DeckLoader from '../DeckLoader'
import { bookingNormalizer } from '../../utils/normalizers'

const renderPageHeader = () => (
  <header>
    <h1>Mes réservations</h1>
  </header>
)

const renderPageFooter = () => {
  const footerProps = { borderTop: true }
  return <Footer {...footerProps} />
}

const renderNoBookingSection = () => (
  <div>
    <p className="nothing">Pas encore de réservation.</p>
    <p className="nothing">
      <Link to="/decouverte" className="button is-primary">
        Allez-y !
      </Link>
    </p>
  </div>
)

const renderBookingList = items => (
  <ul className="bookings">
    {items.map(booking => (
      <BookingItem key={booking.id} booking={booking} />
    ))}
  </ul>
)

class BookingsPage extends Component {
  constructor(props) {
    super(props)
    const { dispatch } = props
    const actions = { requestData }
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
      <Main
        header={renderPageHeader}
        name="bookings"
        footer={renderPageFooter}
        redBg
      >
        {soonBookingsLength > 0 && (
          <div>
            <h4>C&apos;est bientôt !</h4>
            {renderBookingList(soonBookings)}
          </div>
        )}
        {otherBookingsLength > 0 && (
          <div>
            <h4>Réservations</h4>
            {renderBookingList(otherBookings)}
          </div>
        )}
        {hasNoBooking && renderNoBookingSection()}
        <DeckLoader
          isempty={isempty}
          haserror={haserror}
          isloading={isloading}
        />
      </Main>
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
