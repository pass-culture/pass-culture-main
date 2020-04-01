import { connect } from 'react-redux'
import { compose } from 'redux'
import { assignData, deleteData, requestData } from 'redux-thunk-data'
import { saveLastRecommendationsRequestTimestamp } from '../../../reducers/data'
import { updateSeedLastRequestTimestamp } from '../../../reducers/pagination'
import { selectReadRecommendations } from '../../../selectors/data/readRecommendationsSelectors'
import { selectRecommendations } from '../../../selectors/data/recommendationsSelectors'
import { selectSeedLastRequestTimestamp } from '../../../selectors/pagination/paginationSelector'
import getOfferIdAndMediationIdApiPathQueryString from '../../../utils/getOfferIdAndMediationIdApiPathQueryString'
import { recommendationNormalizer } from '../../../utils/normalizers'
import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'
import Discovery from './Discovery'
import selectCurrentRecommendation from './selectors/selectCurrentRecommendation'
import selectTutorials from './selectors/selectTutorials'
import {
  checkIfShouldReloadRecommendationsBecauseOfLongTime,
  isDiscoveryStartupUrl,
} from './utils/utils'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const { params } = match
  const { mediationId, offerId } = params
  const currentRecommendation = selectCurrentRecommendation(state, offerId, mediationId)
  const tutorials = selectTutorials(state)
  const recommendations = selectRecommendations(state)
  const readRecommendations = selectReadRecommendations(state)
  const hasNoRecommendations = recommendations && recommendations.length === 0
  const shouldReloadRecommendations =
    checkIfShouldReloadRecommendationsBecauseOfLongTime(state) || hasNoRecommendations
  const seedLastRequestTimestamp = selectSeedLastRequestTimestamp(state)

  return {
    currentRecommendation,
    readRecommendations,
    recommendations,
    seedLastRequestTimestamp,
    shouldReloadRecommendations,
    tutorials,
  }
}

export const mapDispatchToProps = (dispatch, prevProps) => ({
  deleteTutorials: recommendations => {
    dispatch(deleteData({ recommendations }))
  },
  loadRecommendations: (
    handleSuccess,
    handleFail,
    currentRecommendation,
    recommendations,
    readRecommendations,
    shouldReloadRecommendations
  ) => {
    const { match } = prevProps
    const seenRecommendationIds =
      (shouldReloadRecommendations && []) ||
      (recommendations && recommendations.map(reco => reco.offerId))
    let queryParams = getOfferIdAndMediationIdApiPathQueryString(match, currentRecommendation)

    dispatch(
      requestData({
        apiPath: `/recommendations/v2?${queryParams}`,
        body: {
          readRecommendations,
          seenRecommendationIds,
        },
        handleFail: handleFail,
        handleSuccess: handleSuccess,
        method: 'PUT',
        normalizer: recommendationNormalizer,
      })
    )
  },
  redirectToFirstRecommendationIfNeeded: loadedRecommendations => {
    const { match, history } = prevProps

    if (!loadedRecommendations) {
      return
    }

    const shouldRedirectToFirstRecommendationUrl =
      loadedRecommendations.length > 0 && isDiscoveryStartupUrl(match)
    if (!shouldRedirectToFirstRecommendationUrl) {
      return
    }
    const firstOfferId = loadedRecommendations[0].offerId || 'tuto'
    const firstMediationId = loadedRecommendations[0].mediationId || 'vide'
    history.replace(`/decouverte/${firstOfferId}/${firstMediationId}`)
  },
  resetReadRecommendations: () => {
    dispatch(assignData({ readRecommendations: [] }))
  },
  saveLastRecommendationsRequestTimestamp: () => {
    dispatch(saveLastRecommendationsRequestTimestamp())
  },
  updateLastRequestTimestamp: () => {
    dispatch(updateSeedLastRequestTimestamp(Date.now()))
  },
  resetRecommendations: () => {
    dispatch(assignData({ recommendations: [] }))
  },
})

export default compose(
  withRequiredLogin,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(Discovery)
