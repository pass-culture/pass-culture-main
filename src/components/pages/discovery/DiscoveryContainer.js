import { connect } from 'react-redux'
import { compose } from 'redux'
import { assignData, deleteData, requestData } from 'redux-thunk-data'

import Discovery from './Discovery'
import { checkIfShouldReloadRecommendationsBecauseOfLongTime, isDiscoveryStartupUrl, } from './utils/utils'
import selectCurrentRecommendation from './selectors/selectCurrentRecommendation'
import selectTutorials from './selectors/selectTutorials'
import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'
import getOfferIdAndMediationIdApiPathQueryString from '../../../helpers/getOfferIdAndMediationIdApiPathQueryString'
import { saveLastRecommendationsRequestTimestamp } from '../../../reducers/data'
import { recommendationNormalizer } from '../../../utils/normalizers'
import { selectRecommendations } from '../../../selectors/data/recommendationsSelectors'
import { selectReadRecommendations } from '../../../selectors/data/readRecommendationsSelectors'
import { selectPage, selectSeed } from '../../../selectors/pagination/paginationSelector'
import { updatePage } from '../../../reducers/pagination'

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
    checkIfShouldReloadRecommendationsBecauseOfLongTime(state) ||
    hasNoRecommendations

  return {
    currentRecommendation,
    page,
    readRecommendations,
    recommendations,
    seed,
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
    const seenRecommendationIds = (shouldReloadRecommendations && []) || (recommendations && recommendations.map(reco => reco.id))
    let queryParams = getOfferIdAndMediationIdApiPathQueryString(match, currentRecommendation)

    let newPage
    if (page === 1) {
      newPage = page
    } else {
      newPage = page + 1
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
    dispatch(
      updatePage(newPage)
    )
  },
  redirectHome: () => {
    const { history } = prevProps
    setTimeout(
      () => history.replace('/connexion'),
      2000
    )
  },
  redirectToFirstRecommendationIfNeeded: loadedRecommendations => {
    const { match, history } = prevProps

    if (!loadedRecommendations) {
      return
    }

    const shouldRedirectToFirstRecommendationUrl = loadedRecommendations.length > 0 && isDiscoveryStartupUrl(match)
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
})

export default compose(
  withRequiredLogin,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(Discovery)
