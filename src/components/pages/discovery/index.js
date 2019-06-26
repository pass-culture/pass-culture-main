import { assignData } from 'fetch-normalize-data'
import PropTypes from 'prop-types'
import React, { Fragment } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { Route } from 'react-router-dom'
import { toast } from 'react-toastify'
import { requestData } from 'redux-saga-data'

import DeckContainer from './deck/DeckContainer'
import BookingContainer from '../../booking/BookingContainer'
import { withRequiredLogin } from '../../hocs'
import BackButton from '../../layout/BackButton'
import LoaderContainer from '../../layout/Loader/LoaderContainer'
import Footer from '../../layout/Footer'
import selectCurrentRecommendation from '../../../selectors/currentRecommendation'
import {
  getQueryParams,
  getRouterQueryByKey,
  shouldShowVerso,
} from '../../../helpers'
import { recommendationNormalizer } from '../../../utils/normalizers'

export class RawDiscoveryPage extends React.PureComponent {
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
    this.handleDataRequest()
    const { fromPassword } = this.props
    if (!fromPassword) return
    const delay = 1000
    const autoClose = 3000
    const message = 'Votre mot de passe a bien été enregistré.'
    setTimeout(() => toast(message, { autoClose }), delay)
  }

  componentWillUnmount() {
    const { dispatch } = this.props
    dispatch(assignData({ recommendations: [] }))
  }

  handleRequestFail = () => {
    this.setState({ hasError: true, isLoading: true }, () => {
      const { history } = this.props
      const delayBeforeRedirect = 2000
      setTimeout(() => history.replace('/connexion'), delayBeforeRedirect)
    })
  }

  handleRequestSuccess = (state, action) => {
    const { dispatch, history, recommendations } = this.props
    const {
      payload: { data },
    } = action

    const newRecosNb = data ? data.length : 0
    const pathnameWithoutTrailingSlash = document.location.pathname.replace(
      /\/$/,
      ''
    )
    const weAreNotViewingACard =
      pathnameWithoutTrailingSlash === '/decouverte' ||
      pathnameWithoutTrailingSlash === '/decouverte/tuto/fin'
    const shouldReloadPage = newRecosNb > 0 && weAreNotViewingACard

    const atWorldsEnd = newRecosNb === 0
    const isEmpty = (!recommendations || !recommendations.length) && atWorldsEnd
    this.setState({
      atWorldsEnd,
      isEmpty,
      isLoading: false,
    })

    dispatch(assignData({ readRecommendations: [] }))

    if (!shouldReloadPage) return

    const firstRecommendation = data[0] || {}

    // NOTE -> si la premiere carte n'a pas d'offerid
    // alors il s'agit d'une carte tuto
    const firstOfferId =
      (firstRecommendation && firstRecommendation.offerId) || 'tuto'
    const firstMediationId =
      (firstRecommendation && firstRecommendation.mediationId) || ''
    // replace pluto qu'un push permet de recharger les données
    // quand on fait back dans le navigateur et qu'on revient
    // à l'URL /decouverte
    history.replace(`/decouverte/${firstOfferId}/${firstMediationId}`)
  }

  handleDataRequest = () => {
    const { dispatch, match, recommendations, readRecommendations } = this.props

    const { atWorldsEnd, isLoading } = this.state

    if (atWorldsEnd || isLoading) return

    this.setState({ isLoading: true })
    // recupere les arguments depuis l'URL
    // l'API renvoi cette première carte avant les autres recommendations

    const queryString = getQueryParams(match, readRecommendations)
    const apiPath = `/recommendations?${queryString}`

    dispatch(
      requestData({
        apiPath,
        body: {
          readRecommendations,
          seenRecommendationIds:
            recommendations && recommendations.map(r => r.id),
        },
        handleFail: this.handleRequestFail,
        handleSuccess: this.handleRequestSuccess,
        method: 'PUT',
        normalizer: recommendationNormalizer,
      })
    )
  }

  render() {
    const { match } = this.props
    const { hasError, isEmpty, isLoading } = this.state

    const withBackButton = shouldShowVerso(match)

    return (
      <Fragment>
        <main
          role="main"
          className="discovery-page no-padding page with-footer"
        >
          {withBackButton && <BackButton />}
          {!isEmpty && (
            <Fragment>
              <Route
                key="route-discovery-booking"
                path="/decouverte/:offerId([A-Z0-9]+)/:mediationId([A-Z0-9]+)?/:view(booking)/:bookingId?/:view(cancelled)?/:menu(menu)?"
                render={route => <BookingContainer {...route} />}
              />
              <Route
                key="route-discovery-deck"
                path="/decouverte/:offerId([A-Z0-9]+)/:mediationId([A-Z0-9]+|verso)?/:view(verso|cancelled)?/:bookingId?/:menu(menu)?"
                render={route => (
                  <DeckContainer
                    {...route}
                    handleDataRequest={this.handleDataRequest}
                  />
                )}
              />
            </Fragment>
          )}
          <Footer id="deck-footer" borderTop />
        </main>
        <LoaderContainer
          isEmpty={isEmpty}
          hasError={hasError}
          isLoading={isLoading}
        />
      </Fragment>
    )
  }
}

RawDiscoveryPage.defaultProps = {
  currentRecommendation: null,
  readRecommendations: null,
  recommendations: null,
}

RawDiscoveryPage.propTypes = {
  currentRecommendation: PropTypes.object,
  dispatch: PropTypes.func.isRequired,
  fromPassword: PropTypes.bool.isRequired,
  history: PropTypes.object.isRequired,
  location: PropTypes.object.isRequired,
  match: PropTypes.object.isRequired,
  readRecommendations: PropTypes.array,
  recommendations: PropTypes.array,
}

const mapStateToProps = (state, ownProps) => {
  const { location, match } = ownProps
  const { mediationId, offerId } = match.params
  const from = getRouterQueryByKey(location, 'from')
  const fromPassword = from === 'password'
  return {
    currentRecommendation: selectCurrentRecommendation(
      state,
      offerId,
      mediationId
    ),
    fromPassword,
    readRecommendations: state.data.readRecommendations,
    recommendations: state.data.recommendations,
  }
}

const DiscoveryPage = compose(
  withRequiredLogin,
  connect(mapStateToProps)
)(RawDiscoveryPage)

export default DiscoveryPage
