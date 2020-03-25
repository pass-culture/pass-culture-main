import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import { Route } from 'react-router-dom'

import DeckContainer from './Deck/DeckContainer'
import BookingContainer from '../../layout/Booking/BookingContainer'
import BookingCancellationContainer from '../../layout/BookingCancellation/BookingCancellationContainer'
import AbsoluteFooterContainer from '../../layout/AbsoluteFooter/AbsoluteFooterContainer'
import LoaderContainer from '../../layout/Loader/LoaderContainer'
import isDetailsView from '../../../utils/isDetailsView'
import isCancelView from '../../../utils/isCancelView'
import { MINIMUM_DELAY_BEFORE_UPDATING_SEED_3_HOURS } from './utils/utils'

class Discovery extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      atWorldsEnd: false,
      hasError: false,
      isEmpty: false,
      isLoading: false,
    }
  }

  componentDidMount() {
    const {
      recommendations,
      redirectToFirstRecommendationIfNeeded,
      saveLastRecommendationsRequestTimestamp,
      shouldReloadRecommendations,
    } = this.props

    if (shouldReloadRecommendations) {
      this.updateRecommendations()
      saveLastRecommendationsRequestTimestamp()
    } else {
      redirectToFirstRecommendationIfNeeded(recommendations)
    }
  }

  componentDidUpdate(prevProps) {
    const {
      location,
      recommendations,
      redirectToFirstRecommendationIfNeeded,
      seedLastRequestTimestamp,
      updateLastRequestTimestamp,
    } = this.props
    const { location: prevLocation } = prevProps

    if (prevLocation.pathname !== location.pathname && location.pathname === '/decouverte-v2') {
      redirectToFirstRecommendationIfNeeded(recommendations)
    }

    if (Date.now() > seedLastRequestTimestamp + MINIMUM_DELAY_BEFORE_UPDATING_SEED_3_HOURS) {
      updateLastRequestTimestamp()
    }
  }

  componentWillUnmount() {
    const { deleteTutorials, tutorials, resetRecommendations } = this.props

    if (tutorials.length > 0) {
      deleteTutorials(tutorials)
    }

    resetRecommendations()
  }

  handleFail = () => {
    this.setState({ hasError: true, isLoading: true })
  }

  handleSuccess = (state, action) => {
    const {
      recommendations,
      resetReadRecommendations,
      redirectToFirstRecommendationIfNeeded,
    } = this.props

    const { data: loadedRecommendations = [] } = action && action.payload
    const atWorldsEnd = loadedRecommendations.length === 0
    const isEmpty = (!recommendations || !recommendations.length) && atWorldsEnd

    this.setState({ atWorldsEnd, isEmpty, isLoading: false }, () => {
      resetReadRecommendations()
      redirectToFirstRecommendationIfNeeded(loadedRecommendations)
    })
  }

  updateRecommendations = () => {
    const {
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
        shouldReloadRecommendations
      )
    })
  }

  renderBooking = () => {
    const { currentRecommendation } = this.props
    return <BookingContainer recommendation={currentRecommendation} />
  }

  renderBookingCancellation = () => <BookingCancellationContainer />

  renderDeck = () => <DeckContainer handleRequestPutRecommendations={this.updateRecommendations} />

  render() {
    const { match } = this.props
    const { hasError, isEmpty, isLoading } = this.state
    const cancelView = isCancelView(match)

    return (
      <Fragment>
        {!isEmpty && (
          <main className="discovery-page no-padding page with-footer">
            <Route
              key="route-discovery-deck"
              path="/decouverte-v2/:offerId(tuto|[A-Z0-9]+)/:mediationId(vide|fin|[A-Z0-9]+)/:details(details|transition)?/:booking(reservation)?/:bookingId([A-Z0-9]+)?/:cancellation(annulation)?"
              render={this.renderDeck}
              sensitive
            />
            <Route
              key="route-discovery-booking"
              path="/decouverte-v2/:offerId(tuto|[A-Z0-9]+)/:mediationId(vide|fin|[A-Z0-9]+)/:details(details)/:booking(reservation)/:bookingId([A-Z0-9]+)?/:cancellation(annulation)?/:confirmation(confirmation)?"
              render={cancelView ? this.renderBookingCancellation : this.renderBooking}
              sensitive
            />
            <AbsoluteFooterContainer
              areDetailsVisible={isDetailsView(match)}
              borderTop
              id="deck-footer"
            />
          </main>
        )}
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
  currentRecommendation: null,
  readRecommendations: null,
  recommendations: null,
}

Discovery.propTypes = {
  currentRecommendation: PropTypes.shape(),
  deleteTutorials: PropTypes.func.isRequired,
  loadRecommendations: PropTypes.func.isRequired,
  location: PropTypes.shape({
    pathname: PropTypes.string.isRequired,
  }).isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      view: PropTypes.string,
    }),
  }).isRequired,
  readRecommendations: PropTypes.arrayOf(PropTypes.shape()),
  recommendations: PropTypes.arrayOf(PropTypes.shape()),
  redirectToFirstRecommendationIfNeeded: PropTypes.func.isRequired,
  resetReadRecommendations: PropTypes.func.isRequired,
  resetRecommendations: PropTypes.func.isRequired,
  saveLastRecommendationsRequestTimestamp: PropTypes.func.isRequired,
  seedLastRequestTimestamp: PropTypes.number.isRequired,
  shouldReloadRecommendations: PropTypes.bool.isRequired,
  tutorials: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  updateLastRequestTimestamp: PropTypes.func.isRequired,
}

export default Discovery
