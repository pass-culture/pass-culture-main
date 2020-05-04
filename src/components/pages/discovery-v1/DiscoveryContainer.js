import { connect } from 'react-redux'
import { compose } from 'redux'
import { assignData, requestData } from 'redux-thunk-data'
import { selectReadRecommendations } from '../../../redux/selectors/data/readRecommendationsSelectors'
import { selectRecommendations } from '../../../redux/selectors/data/recommendationsSelectors'
import { selectSeedLastRequestTimestamp } from '../../../redux/selectors/pagination/paginationSelector'
import getOfferIdAndMediationIdApiPathQueryString from '../../../utils/getOfferIdAndMediationIdApiPathQueryString'
import { recommendationNormalizer } from '../../../utils/normalizers'
import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'
import Discovery from './Discovery'
import selectCurrentRecommendation from './selectors/selectCurrentRecommendation'
import {
  checkIfShouldReloadRecommendationsBecauseOfLongTime,
  isDiscoveryStartupUrl,
} from './utils/utils'
import { saveLastRecommendationsRequestTimestamp } from '../../../redux/actions/lastRecommendationsRequestTimestamp'
import { updateSeedLastRequestTimestamp } from '../../../redux/actions/pagination'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const { params } = match
  const { mediationId, offerId } = params
  const currentRecommendation = selectCurrentRecommendation(state, offerId, mediationId)
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
  }
}

export const mapDispatchToProps = (dispatch, prevProps) => ({
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
    const firstOfferId = loadedRecommendations[0].offerId
    const firstMediationId = loadedRecommendations[0].mediationId
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
})

export default compose(
  withRequiredLogin,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(Discovery)
