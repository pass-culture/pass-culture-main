import PropTypes from 'prop-types'
import React, { Fragment } from 'react'
import { Route } from 'react-router-dom'

import DeckContainer from './deck/DeckContainer'
import BookingContainer from '../../booking/BookingContainer'
import BackLink from '../../layout/Header/BackLink'
import LoaderContainer from '../../layout/Loader/LoaderContainer'
import Footer from '../../layout/Footer'

class Discovery extends React.PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      atWorldsEnd: false,
      hasError: false,
      isEmpty: null,
      isLoading: false,
    }
  }

  componentDidMount() {
    const {
      recommendations,
      saveLoadRecommendationsTimestamp,
      redirectToFirstRecommendationIfNeeded,
      shouldReloadRecommendations,
      showPasswordChangedPopin,
    } = this.props
    showPasswordChangedPopin()
    if (shouldReloadRecommendations) {
      this.onHandleDataRequest()
      saveLoadRecommendationsTimestamp()
    } else {
      redirectToFirstRecommendationIfNeeded(recommendations)
    }
  }

  componentDidUpdate(prevProps) {
    const { location, recommendations, redirectToFirstRecommendationIfNeeded } = this.props
    const { location: prevLocation } = prevProps
    if (prevLocation.pathname !== location.pathname && location.pathname === '/decouverte') {
      redirectToFirstRecommendationIfNeeded(recommendations)
    }
  }

  handleRequestFail = () => {
    const { onRequestFailRedirectToHome } = this.props
    const nextState = { hasError: true, isLoading: true }
    this.setState(nextState, onRequestFailRedirectToHome)
  }

  handleRequestSuccess = (state, action) => {
    const {
      recommendations,
      resetReadRecommendations,
      redirectToFirstRecommendationIfNeeded,
    } = this.props

    const { data: loadedRecommendations } = (action && action.payload) || []
    const loadedRecommendationsLength = loadedRecommendations.length

    const isLoading = false
    const atWorldsEnd = loadedRecommendationsLength === 0
    const isEmpty = (!recommendations || !recommendations.length) && atWorldsEnd
    const nextState = { atWorldsEnd, isEmpty, isLoading }

    this.setState(nextState, () => {
      resetReadRecommendations()
      redirectToFirstRecommendationIfNeeded(loadedRecommendations)
    })
  }

  onHandleDataRequest = () => {
    const {
      recommendations,
      readRecommendations,
      loadRecommendations,
      shouldReloadRecommendations,
    } = this.props

    const { atWorldsEnd, isLoading } = this.state
    const shouldNotLoadRecommendations = atWorldsEnd || isLoading
    if (shouldNotLoadRecommendations) return

    const nextState = { isLoading: true }
    this.setState(nextState, () => {
      loadRecommendations(
        this.handleRequestSuccess,
        this.handleRequestFail,
        recommendations,
        readRecommendations,
        shouldReloadRecommendations
      )
    })
  }

  rendeBookingRoute = route => <BookingContainer {...route} />

  renderDeckROute = route => (
    <DeckContainer
      {...route}
      handleDataRequest={this.onHandleDataRequest}
    />
  )

  render() {
    const { hasError, isEmpty, isLoading } = this.state
    const { match } = this.props

    return (
      <Fragment>
        <main
          className="discovery-page no-padding page with-footer"
          role="main"
        >
          {(match.params.view === 'verso' || match.params.mediationId === 'verso') && (
            <BackLink backTo="/reservations" />
          )}
          {!isEmpty && (
            <Fragment>
              <Route
                key="route-discovery-booking"
                path="/decouverte/:offerId([A-Z0-9]+)/:mediationId([A-Z0-9]+)?/:view(booking)/:bookingId?/:view(cancelled)?/:menu(menu)?"
                render={this.rendeBookingRoute}
              />
              <Route
                key="route-discovery-deck"
                path="/decouverte/:offerId([A-Z0-9]+)/:mediationId([A-Z0-9]+|verso)?/:view(verso|cancelled)?/:bookingId?/:menu(menu)?"
                render={this.renderDeckROute}
              />
            </Fragment>
          )}
          <Footer
            borderTop
            id="deck-footer"
          />
        </main>
        <LoaderContainer
          hasError={hasError}
          isEmpty={isEmpty}
          isLoading={isLoading}
        />
      </Fragment>
    )
  }
}

Discovery.defaultProps = {
  readRecommendations: null,
  recommendations: null,
  withBackButton: false,
}

Discovery.propTypes = {
  loadRecommendations: PropTypes.func.isRequired,
  location: PropTypes.shape().isRequired,
  match: PropTypes.shape().isRequired,
  onRequestFailRedirectToHome: PropTypes.func.isRequired,
  readRecommendations: PropTypes.arrayOf(PropTypes.shape()),
  recommendations: PropTypes.arrayOf(PropTypes.shape()),
  redirectToFirstRecommendationIfNeeded: PropTypes.func.isRequired,
  resetReadRecommendations: PropTypes.func.isRequired,
  resetRecommendations: PropTypes.func.isRequired,
  saveLoadRecommendationsTimestamp: PropTypes.func.isRequired,
  shouldReloadRecommendations: PropTypes.bool.isRequired,
  showPasswordChangedPopin: PropTypes.func.isRequired,
  withBackButton: PropTypes.bool,
}

export default Discovery
