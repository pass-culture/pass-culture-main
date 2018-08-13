import PropTypes from 'prop-types'
import get from 'lodash.get'
import {
  closeLoading,
  requestData,
  showLoading,
  Logger,
} from 'pass-culture-shared'
import React from 'react'
import { connect } from 'react-redux'
import { Route, Switch } from 'react-router-dom'
import { bindActionCreators } from 'redux'

import Deck from '../Deck'
import Main from '../layout/Main'
import Footer from '../layout/Footer'
import DeckLoader from '../DeckLoader'
import currentRecommendationSelector from '../../selectors/currentRecommendation'
import { getDiscoveryQueryParams } from '../../helpers'
import { recommendationNormalizer } from '../../utils/normalizers'

const renderPageFooter = () => {
  const footerProps = { borderTop: true }
  return <Footer {...footerProps} />
}

class DiscoveryPage extends React.PureComponent {
  constructor(props) {
    super(props)
    const { dispatch } = props
    this.state = { isempty: false, isloading: true }
    const actions = { closeLoading, requestData, showLoading }
    this.actions = bindActionCreators(actions, dispatch)
  }

  componentDidMount() {
    Logger.log('DiscoveryPage ---> componentDidMount')
  }

  componentWillUnmount() {
    Logger.log('DiscoveryPage ---> componentWillUnmount')
  }

  handleRequestSuccess = (state, action) => {
    const { history, match } = this.props
    const { offerId } = match.params
    const len = get(action, 'data.length')
    const isempty = !(len && len > 0)
    this.setState({ isempty, isloading: false })
    if (isempty || offerId) return
    // si aucune carte n'est chargée
    // on affiche le tuto
    // ou la premiere carte dans le paylod
    const firstOfferId = get(action, 'data.0.offerId') || 'tuto'
    if (!firstOfferId) {
      Logger.warn('first recommendation has no offer id, weird...')
    }
    const firstMediationId = get(action, 'data.0.mediationId') || ''
    // FIXME -> appeller une action pour le changement de page
    // qui s'occupera d'enregistrer la derniere carte decouverte vue
    history.push(`/decouverte/${firstOfferId}/${firstMediationId}`)
  }

  handleDataRequest = () => {
    // se recharge apres chaque changement de page d'application
    // c'est le comportement normal attendu
    // puisqu'on ne stocke nulle part la page en cours
    const { match } = this.props
    // si les recommendations ont déjà été chargées
    // on ne relance pas de requêtes
    this.setState({ isloading: true })
    // si il existe quelque chose dans l'URL
    // l'API renvoi cette première carte avant les autres recommendations
    const query = getDiscoveryQueryParams(match)
    console.log('match', match)
    console.log('query', query)
    const serviceuri = `recommendations?${query}`
    this.actions.requestData('PUT', serviceuri, {
      handleSuccess: this.handleRequestSuccess,
      normalizer: recommendationNormalizer,
    })
  }

  /*
  handleRedirectFromLoading(props) {
    const { history, mediationId, offerId, recommendations } = props
    if (
      !recommendations ||
      recommendations.length === 0 ||
      mediationId ||
      offerId
    )
      return

    const targetRecommendation = recommendations[0]
    // NOW CHOOSE AN OFFER AMONG THE ONES
    const recommendationOffers = targetRecommendation.recommendationOffers
    const chosenOffer =
      recommendationOffers &&
      recommendationOffers[
        Math.floor(Math.random() * recommendationOffers.length)
      ]

    // PUSH
    const path = getDiscoveryPath(chosenOffer, targetRecommendation.mediation)
    history.push(path)
  }

  componentWillMount() {
    // this.handleRedirectFromLoading(this.props)
    // this.ensureRecommendations(this.props)
  }

  componentWillReceiveProps(nextProps) {
    // this.handleRedirectFromLoading(nextProps)
    if (nextProps.offerId && nextProps.offerId !== this.props.offerId) {
      // this.ensureRecommendations(nextProps)
    }
  }
  */

  render() {
    const { backButton } = this.props
    const { isempty, isloading } = this.state
    return (
      <Main
        noPadding
        name="discovery"
        handleDataRequest={this.handleDataRequest}
        footer={renderPageFooter}
        backButton={backButton ? { className: 'discovery' } : null}
      >
        <Switch>
          <Route
            key="route-discovery-deck"
            path="/decouverte/:offerId/:mediationId?"
            component={Deck}
          />
        </Switch>
        <DeckLoader isempty={isempty} isloading={isloading} />
      </Main>
    )
  }
}

DiscoveryPage.defaultProps = {
  currentRecommendation: null,
  recommendations: null,
}

DiscoveryPage.propTypes = {
  backButton: PropTypes.bool.isRequired,
  dispatch: PropTypes.func.isRequired,
  history: PropTypes.object.isRequired,
  match: PropTypes.object.isRequired,
}

const mapStateToProps = (state, ownProps) => {
  const { mediationId, offerId } = ownProps.match.params
  const currentRecommendation = currentRecommendationSelector(
    state,
    offerId,
    mediationId
  )
  return {
    backButton: ownProps.location.search.indexOf('to=verso') > -1,
    currentRecommendation,
  }
}

export default connect(mapStateToProps)(DiscoveryPage)
