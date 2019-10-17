import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import { Route } from 'react-router-dom'

import DeckContainer from './Deck/DeckContainer'
import BookingContainer from '../Booking/BookingContainer'
import BookingCancellationContainer from '../BookingCancellation/BookingCancellationContainer'
import AbsoluteFooterContainer from '../../layout/AbsoluteFooter/AbsoluteFooterContainer'
import LoaderContainer from '../../layout/Loader/LoaderContainer'
import isDetailsView from '../../../helpers/isDetailsView'
import getIsConfirmingCancelling from '../../../helpers/getIsConfirmingCancelling'

class Discovery extends PureComponent {
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
      this.onRequestPutRecommendations()
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

  componentWillUnmount() {
    const { deleteTutos, tutos } = this.props
    if (tutos.length > 0) {
      deleteTutos(tutos)
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

  onRequestPutRecommendations = () => {
    const {
      currentRecommendation,
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
        currentRecommendation,
        recommendations,
        readRecommendations,
        shouldReloadRecommendations
      )
    })
  }

  renderBookingOrCancellation = route => {
    const { match } = this.props
    const isConfirmingCancelling = getIsConfirmingCancelling(match)
    return isConfirmingCancelling
      ? this.renderBookingCancellation(route)
      : this.renderBooking(route)
  }

  renderBookingCancellation = route => {
    return <BookingCancellationContainer {...route} />
  }

  renderBooking = route => {
    const { currentRecommendation } = this.props
    return (<BookingContainer
      {...route}
      recommendation={currentRecommendation}
            />)
  }

  renderDeck = route => (
    <DeckContainer
      {...route}
      handleRequestPutRecommendations={this.onRequestPutRecommendations}
    />
  )

  render() {
    const { match } = this.props
    const { hasError, isEmpty, isLoading } = this.state

    return (
      <Fragment>
        <main className="discovery-page no-padding page with-footer">
          {!isEmpty && (
            <Fragment>
              <Route
                key="route-discovery-deck"
                path="/decouverte/:offerId(tuto|[A-Z0-9]+)/:mediationId(vide|fin|[A-Z0-9]+)/:details(details|transition)?/:booking(reservation)?/:bookingId(creation|[A-Z0-9]+)?/:cancellation(annulation)?/:menu(menu)?"
                render={this.renderDeck}
              />
              <Route
                key="route-discovery-booking"
                path="/decouverte/:offerId(tuto|[A-Z0-9]+)/:mediationId(vide|fin|[A-Z0-9]+)/:details(details)/:booking(reservation)/:bookingId(creation|[A-Z0-9]+)?/:cancellation(annulation)?/:confirmation(confirmation)?/:menu(menu)?"
                render={this.renderBookingOrCancellation}
              />
            </Fragment>
          )}
          <AbsoluteFooterContainer
            areDetailsVisible={isDetailsView(match)}
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
  currentRecommendation: null,
  readRecommendations: null,
  recommendations: null,
}

Discovery.propTypes = {
  currentRecommendation: PropTypes.shape(),
  deleteTutos: PropTypes.func.isRequired,
  loadRecommendations: PropTypes.func.isRequired,
  location: PropTypes.shape({
    pathname: PropTypes.string.isRequired,
  }).isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      view: PropTypes.string,
    }),
  }).isRequired,
  onRequestFailRedirectToHome: PropTypes.func.isRequired,
  readRecommendations: PropTypes.arrayOf(PropTypes.shape()),
  recommendations: PropTypes.arrayOf(PropTypes.shape()),
  redirectToFirstRecommendationIfNeeded: PropTypes.func.isRequired,
  resetReadRecommendations: PropTypes.func.isRequired,
  saveLoadRecommendationsTimestamp: PropTypes.func.isRequired,
  shouldReloadRecommendations: PropTypes.bool.isRequired,
  showPasswordChangedPopin: PropTypes.func.isRequired,
  tutos: PropTypes.arrayOf(PropTypes.shape()).isRequired,
}

export default Discovery
