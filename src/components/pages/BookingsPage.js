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
import DeckLoader from '../deck/DeckLoader'
import { toggleMainMenu } from '../../reducers/menu'
import ProfilePicture from '../layout/ProfilePicture'
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
    {items.map(booking => (
      <React.Fragment>
        <BookingItem key={booking.id} booking={booking} />
      </React.Fragment>
    ))}
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
      <div id="bookings-page" className="page is-relative flex-rows red-bg">
        {!isloading && (
          <React.Fragment>
            <header className="padded has-text-centered flex-0 fs19">
              <h1>Mes réservations</h1>
            </header>
            <main role="main" className="application-main flex-rows flex-start">
              <Scrollbars>
                {soonBookingsLength > 0 && (
                  <div>
                    <h4 className="mb16 fs19 is-uppercase">
                      <i>C&apos;est bientôt !</i>
                    </h4>
                    {renderBookingList(soonBookings)}
                  </div>
                )}
                {otherBookingsLength > 0 && (
                  <div>
                    <h4 className="mb16 fs19 is-uppercase">
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
            <footer
              role="navigation"
              className="application-footer dotted-top flex-columns items-center flex-center flex-0"
            >
              <button
                className="profile-button no-border no-background"
                onClick={this.actions.toggleMainMenu}
                type="button"
              >
                <ProfilePicture alt="Mon menu" />
              </button>
            </footer>
          </React.Fragment>
        )}
        {/*
          FIXME: le isempty a pas de sens ici
          Dans tous les cas on affiche un écran si il n'y pas de réservations
        */}
        {!isempty && <DeckLoader haserror={haserror} isloading={isloading} />}
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
