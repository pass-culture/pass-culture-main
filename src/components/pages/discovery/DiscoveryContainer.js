import { connect } from 'react-redux'
import { compose } from 'redux'
import { toast } from 'react-toastify'
import { assignData } from 'fetch-normalize-data'
import { requestData } from 'redux-saga-data'

import Discovery from './Discovery'
import { checkIfShouldReloadRecommendations, isDiscoveryStartupPathname } from './utils'
import { withRequiredLogin } from '../../hocs'
import { getQueryParams, getRouterQueryByKey, shouldShowVerso } from '../../../helpers'
import { recommendationNormalizer } from '../../../utils/normalizers'
import { saveLastRecommendationsRequestTimestamp } from '../../../reducers/data'

export const mapStateToProps = (state, props) => {
  const { match } = props
  const withBackButton = shouldShowVerso(match)
  const { readRecommendations, recommendations } = (state && state.data) || {}
  const shouldReloadRecommendations =
    checkIfShouldReloadRecommendations(state) || (recommendations && recommendations.length <= 0)
  return {
    readRecommendations,
    recommendations,
    shouldReloadRecommendations,
    withBackButton,
  }
}

export const mapDispatchToProps = (dispatch, props) => ({
  loadRecommendations: (
    handleRequestSuccess,
    handleRequestFail,
    recommendations,
    readRecommendations,
    shouldReloadRecommendations
  ) => {
    const { match } = props
    const queryString = getQueryParams(match, readRecommendations)
    const apiPath = `/recommendations?${queryString}`
    const seenRecommendationIds =
      (shouldReloadRecommendations && []) || (recommendations && recommendations.map(r => r.id))
    dispatch(
      requestData({
        apiPath,
        body: { readRecommendations, seenRecommendationIds },
        handleFail: handleRequestFail,
        handleSuccess: handleRequestSuccess,
        method: 'PUT',
        normalizer: recommendationNormalizer,
      })
    )
  },

  onRequestFailRedirectToHome: () => {
    const { history } = props
    const delayBeforeRedirect = 2000
    setTimeout(() => history.replace('/connexion'), delayBeforeRedirect)
  },

  redirectToFirstRecommendationIfNeeded: loadedRecommendations => {
    const { history, location } = props

    const shouldReloadPage =
      loadedRecommendations.length > 0 && isDiscoveryStartupPathname(location.pathname)

    if (!shouldReloadPage) return

    const firstRecommendation = loadedRecommendations[0] || false
    const firstOfferId = (firstRecommendation && firstRecommendation.offerId) || 'tuto'
    const firstMediationId = (firstRecommendation && firstRecommendation.mediationId) || ''
    // replace pluto qu'un push permet de recharger les données
    // quand on fait back dans le navigateur et qu'on revient
    // à l'URL /decouverte
    history.replace(`/decouverte/${firstOfferId}/${firstMediationId}`)
  },

  resetReadRecommendations: () => {
    dispatch(assignData({ readRecommendations: [] }))
  },

  resetRecommendations: () => {
    dispatch(assignData({ recommendations: [] }))
  },

  saveLoadRecommendationsTimestamp: () => {
    dispatch(saveLastRecommendationsRequestTimestamp())
  },

  showPasswordChangedPopin: () => {
    const { location } = props
    const from = getRouterQueryByKey(location, 'from')
    const fromPassword = from === 'password'
    if (!fromPassword) return
    const delay = 1000
    const autoClose = 3000
    const message = 'Votre mot de passe a bien été enregistré.'
    setTimeout(() => toast(message, { autoClose }), delay)
  },
})

export default compose(
  withRequiredLogin,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(Discovery)
