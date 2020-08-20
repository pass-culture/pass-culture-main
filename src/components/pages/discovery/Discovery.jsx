import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import { Route, Switch } from 'react-router-dom'

import BookingContainer from '../../layout/Booking/BookingContainer'
import BookingCancellationContainer from '../../layout/BookingCancellation/BookingCancellationContainer'
import { ApiError } from '../../layout/ErrorBoundaries/ErrorsPage/ApiError'
import PageNotFoundContainer from '../../layout/ErrorBoundaries/ErrorsPage/PageNotFound/PageNotFoundContainer'
import LoaderContainer from '../../layout/Loader/LoaderContainer'
import DeckContainer from './Deck/DeckContainer'
import { MINIMUM_DELAY_BEFORE_UPDATING_SEED_3_HOURS } from './utils/utils'

class Discovery extends PureComponent {
  constructor(props) {
    super(props)

    this.state = {
      atWorldsEnd: false,
      isLoading: false,
    }
  }

  componentDidMount() {
    const {
      recommendations,
      redirectToFirstRecommendationIfNeeded,
      saveLastRecommendationsRequestTimestamp,
      shouldReloadRecommendations,
      coordinates,
      trackGeolocation,
    } = this.props

    const isGeolocated = coordinates && coordinates.latitude && coordinates.longitude
    if (isGeolocated) {
      trackGeolocation()
    }

    if (shouldReloadRecommendations) {
      this.updateRecommendations()
      saveLastRecommendationsRequestTimestamp()
    } else {
      redirectToFirstRecommendationIfNeeded(recommendations)
    }
  }

  componentDidUpdate(prevProps) {
    const {
      history,
      location,
      recommendations,
      redirectToFirstRecommendationIfNeeded,
      match,
      seedLastRequestTimestamp,
      updateLastRequestTimestamp,
    } = this.props
    const { location: prevLocation, recommendations: prevRecommendations } = prevProps

    if (prevLocation.pathname !== location.pathname && location.pathname === '/decouverte') {
      redirectToFirstRecommendationIfNeeded(recommendations)
    }

    if (Date.now() > seedLastRequestTimestamp + MINIMUM_DELAY_BEFORE_UPDATING_SEED_3_HOURS) {
      updateLastRequestTimestamp()
    }

    if (prevRecommendations !== recommendations) {
      const { params } = match
      const { offerId } = params
      const isOfferInReco = recommendations.filter(reco => reco.offerId === offerId).length > 0
      if (recommendations.length > 0 && !isOfferInReco) {
        history.push('/decouverte')
      }
    }
  }

  componentWillUnmount() {
    const { resetRecommendations } = this.props
    resetRecommendations()
  }

  handleFail = (state, action) => {
    this.setState(() => {
      throw new ApiError(action.payload.status)
    })
  }

  handleSuccess = (state, action) => {
    const { resetReadRecommendations, redirectToFirstRecommendationIfNeeded } = this.props

    const { data: loadedRecommendations = [] } = action && action.payload
    const atWorldsEnd = loadedRecommendations.length === 0

    this.setState({ atWorldsEnd, isLoading: false }, () => {
      resetReadRecommendations()
      redirectToFirstRecommendationIfNeeded(loadedRecommendations)
    })
  }

  updateRecommendations = () => {
    const {
      coordinates,
      currentRecommendation,
      loadRecommendations,
      readRecommendations,
      recommendations,
      shouldReloadRecommendations,
    } = this.props

    const { atWorldsEnd, isLoading } = this.state
    if (atWorldsEnd || isLoading) {
      return
    }

    this.setState({ isLoading: true }, () => {
      loadRecommendations(
        this.handleSuccess,
        this.handleFail,
        currentRecommendation,
        recommendations,
        readRecommendations,
        shouldReloadRecommendations,
        coordinates
      )
    })
  }

  render() {
    const { currentRecommendation, match } = this.props
    const { isLoading } = this.state

    return (
      <Fragment>
        {isLoading && <LoaderContainer />}

        {!isLoading && (
          <main className="discovery-page no-padding page">
            <Switch>
              <Route
                exact
                path={`${match.path}/:details(details|transition)?/:booking(reservation)?/:bookingId([A-Z0-9]+)?/:cancellation(annulation)?/:confirmation(confirmation)?`}
                sensitive
              >
                <Route
                  exact
                  path={`${match.path}/:details(details|transition)?/:booking(reservation)?/:bookingId([A-Z0-9]+)?/:cancellation(annulation)?`}
                  sensitive
                >
                  <DeckContainer handleRequestPutRecommendations={this.updateRecommendations} />
                </Route>
                <Route
                  exact
                  path={`${match.path}/:details(details)/:booking(reservation)/:bookingId([A-Z0-9]+)?`}
                  sensitive
                >
                  <BookingContainer recommendation={currentRecommendation} />
                </Route>
                <Route
                  exact
                  path={`${match.path}/:details(details)/:booking(reservation)/:bookingId([A-Z0-9]+)/:cancellation(annulation)/:confirmation(confirmation)`}
                  sensitive
                >
                  <BookingCancellationContainer />
                </Route>
              </Route>
              <Route>
                <PageNotFoundContainer />
              </Route>
            </Switch>
          </main>
        )}
      </Fragment>
    )
  }
}

Discovery.defaultProps = {
  currentRecommendation: null,
  readRecommendations: null,
  recommendations: null,
}

Discovery.propTypes = {
  coordinates: PropTypes.shape().isRequired,
  currentRecommendation: PropTypes.shape(),
  history: PropTypes.shape().isRequired,
  loadRecommendations: PropTypes.func.isRequired,
  location: PropTypes.shape({
    pathname: PropTypes.string.isRequired,
  }).isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      view: PropTypes.string,
      offerId: PropTypes.string,
    }),
    path: PropTypes.string.isRequired,
  }).isRequired,
  readRecommendations: PropTypes.arrayOf(PropTypes.shape()),
  recommendations: PropTypes.arrayOf(PropTypes.shape()),
  redirectToFirstRecommendationIfNeeded: PropTypes.func.isRequired,
  resetReadRecommendations: PropTypes.func.isRequired,
  resetRecommendations: PropTypes.func.isRequired,
  saveLastRecommendationsRequestTimestamp: PropTypes.func.isRequired,
  seedLastRequestTimestamp: PropTypes.number.isRequired,
  shouldReloadRecommendations: PropTypes.bool.isRequired,
  trackGeolocation: PropTypes.func.isRequired,
  updateLastRequestTimestamp: PropTypes.func.isRequired,
}

export default Discovery
