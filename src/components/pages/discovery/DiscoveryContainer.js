import { connect } from 'react-redux'
import { compose } from 'redux'
import { toast } from 'react-toastify'
import { assignData, deleteData, requestData } from 'redux-thunk-data'

import Discovery from './Discovery'
import {
  checkIfShouldReloadRecommendationsBecauseOfLongTime,
  isDiscoveryStartupUrl,
} from './utils/utils'
import selectCurrentRecommendation from './selectors/selectCurrentRecommendation'
import selectTutos from './selectors/selectTutos'
import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'
import getOfferIdAndMediationIdApiPathQueryString from '../../../helpers/getOfferIdAndMediationIdApiPathQueryString'
import { saveLastRecommendationsRequestTimestamp } from '../../../reducers/data'
import { recommendationNormalizer } from '../../../utils/normalizers'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const { params } = match
  const { mediationId, offerId } = params
  const currentRecommendation = selectCurrentRecommendation(state, offerId, mediationId)
  const tutos = selectTutos(state)
  const { readRecommendations, recommendations } = (state && state.data) || {}
  const shouldReloadRecommendations =
    checkIfShouldReloadRecommendationsBecauseOfLongTime(state) ||
    (recommendations && recommendations.length <= 0)
  return {
    currentRecommendation,
    readRecommendations,
    recommendations,
    shouldReloadRecommendations,
    tutos,
  }
}

export const mapDispatchToProps = (dispatch, props) => ({
  deleteTutos: recommendations => {
    dispatch(deleteData({ recommendations }))
  },

  loadRecommendations: (
    handleRequestSuccess,
    handleRequestFail,
    currentRecommendation,
    recommendations,
    readRecommendations,
    shouldReloadRecommendations
  ) => {
    const { match } = props
    const queryString = getOfferIdAndMediationIdApiPathQueryString(match, currentRecommendation)
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
    const { match, history } = props

    if (!loadedRecommendations) {
      return
    }

    const shouldRedirectToFirstRecommendationUrl =
      loadedRecommendations.length > 0 && isDiscoveryStartupUrl(match)

    if (!shouldRedirectToFirstRecommendationUrl) return

    const firstOfferId = loadedRecommendations[0].offerId || 'tuto'
    const firstMediationId = loadedRecommendations[0].mediationId || 'vide'

    // replace pluto qu'un push permet de recharger les données
    // quand on fait back dans le navigateur et qu'on revient
    // à l'URL /decouverte
    history.replace(`/decouverte/${firstOfferId}/${firstMediationId}`)
  },

  resetReadRecommendations: () => {
    dispatch(assignData({ readRecommendations: [] }))
  },

  saveLoadRecommendationsTimestamp: () => {
    dispatch(saveLastRecommendationsRequestTimestamp())
  },

  showPasswordChangedPopin: () => {
    const { query } = props
    const queryParams = query.parse()
    const { from } = queryParams
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
