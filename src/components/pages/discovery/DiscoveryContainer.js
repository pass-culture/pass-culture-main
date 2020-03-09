import { connect } from 'react-redux'
import { compose } from 'redux'
import { assignData, deleteData, requestData } from 'redux-thunk-data'
import { saveLastRecommendationsRequestTimestamp } from '../../../reducers/data'
import {
  updatePage,
  updateSeed,
  updateSeedLastRequestTimestamp,
} from '../../../reducers/pagination'
import { selectReadRecommendations } from '../../../selectors/data/readRecommendationsSelectors'
import { selectRecommendations } from '../../../selectors/data/recommendationsSelectors'
import {
  selectPage,
  selectSeed,
  selectSeedLastRequestTimestamp,
} from '../../../selectors/pagination/paginationSelector'
import getOfferIdAndMediationIdApiPathQueryString, {
  DEFAULT_VIEW_IDENTIFIERS,
} from '../../../utils/getOfferIdAndMediationIdApiPathQueryString'
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
  const page = selectPage(state)
  const seed = selectSeed(state)
  const hasNoRecommendations = recommendations && recommendations.length === 0
  const shouldReloadRecommendations =
    checkIfShouldReloadRecommendationsBecauseOfLongTime(state) || hasNoRecommendations
  const seedLastRequestTimestamp = selectSeedLastRequestTimestamp(state)

  return {
    currentRecommendation,
    page,
    readRecommendations,
    recommendations,
    seed,
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
    page,
    recommendations,
    readRecommendations,
    seed,
    shouldReloadRecommendations
  ) => {
    const { match } = prevProps
    const seenRecommendationIds =
      (shouldReloadRecommendations && []) ||
      (recommendations && recommendations.map(reco => reco.id))
    let queryParams = getOfferIdAndMediationIdApiPathQueryString(match, currentRecommendation)

    let newPage = page
    const currentRecommendationIsNotEmpty =
      currentRecommendation && Object.keys(currentRecommendation).length > 0
    if (currentRecommendationIsNotEmpty) {
      if (!DEFAULT_VIEW_IDENTIFIERS.includes(currentRecommendation.mediationId)) {
        newPage = page + 1
      }
    }
    let paginationParams = `&page=${newPage}&seed=${seed}`

    dispatch(
      requestData({
        apiPath: `/recommendations?${queryParams}${paginationParams}`,
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
    dispatch(updatePage(newPage))
  },
  redirectHome: () => {
    const { history } = prevProps
    setTimeout(() => history.replace('/connexion'), 2000)
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
  updatePageAndSeedAndLastRequestTimestamp: () => {
    dispatch(updateSeedLastRequestTimestamp(Date.now()))
    dispatch(updateSeed(Math.random()))
    dispatch(updatePage(1))
  },
})

export default compose(
  withRequiredLogin,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(Discovery)
