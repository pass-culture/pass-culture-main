import { connect } from 'react-redux'
import { compose } from 'redux'

import { saveLastRecommendationsRequestTimestamp } from '../../../redux/actions/lastRecommendationsRequestTimestamp'
import { updateSeedLastRequestTimestamp } from '../../../redux/actions/pagination'
import { selectReadRecommendations } from '../../../redux/selectors/data/readRecommendationsSelectors'
import { selectRecommendations } from '../../../redux/selectors/data/recommendationsSelectors'
import { selectUserGeolocation } from '../../../redux/selectors/geolocationSelectors'
import { selectSeedLastRequestTimestamp } from '../../../redux/selectors/pagination/paginationSelector'
import withGeolocationTracking from '../../../tracking/withGeolocationTracking'
import { assignData } from '../../../utils/fetch-normalize-data/reducers/data/actionCreators'
import { requestData } from '../../../utils/fetch-normalize-data/requestData'
import { recommendationNormalizer } from '../../../utils/normalizers'
import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'
import Discovery from './Discovery'
import selectCurrentRecommendation from './selectors/selectCurrentRecommendation'
import { getCoordinatesApiPathQueryString } from './utils/buildApiPathQueryString'
import {
  checkIfShouldReloadRecommendationsBecauseOfLongTime,
  isDiscoveryStartupUrl,
} from './utils/utils'

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
  const coordinates = selectUserGeolocation(state)

  return {
    coordinates,
    currentRecommendation,
    readRecommendations,
    recommendations,
    seedLastRequestTimestamp,
    shouldReloadRecommendations,
  }
}

export const getCurrentPosition = coordinates => {
  if (areValidCoordinates(coordinates)) {
    return Promise.resolve({ coords: coordinates })
  }
  if (navigator.geolocation) {
    return new Promise((resolve, reject) =>
      navigator.geolocation.getCurrentPosition(resolve, reject)
    )
  } else {
    return Promise.reject(new Error('Geolocation not supported'))
  }
}

function getRecommendationsFromAPI(
  userCoordinates,
  dispatch,
  readRecommendations,
  offersSentInLastCall,
  handleFail,
  handleSuccess
) {
  let queryParams = getCoordinatesApiPathQueryString(userCoordinates)

  dispatch(
    requestData({
      apiPath: `/recommendations?${queryParams}`,
      body: {
        readRecommendations,
        offersSentInLastCall,
      },
      handleFail: handleFail,
      handleSuccess: handleSuccess,
      method: 'PUT',
      normalizer: recommendationNormalizer,
    })
  )
}

function areValidCoordinates(coordinates) {
  return coordinates && coordinates.latitude && coordinates.longitude
}

export const mapDispatchToProps = (dispatch, prevProps) => ({
  loadRecommendations: async (
    handleSuccess,
    handleFail,
    currentRecommendation,
    recommendations,
    readRecommendations,
    shouldReloadRecommendations,
    coordinates
  ) => {
    const offersSentInLastCall =
      (shouldReloadRecommendations && []) ||
      (recommendations && recommendations.map(reco => reco.offerId))

    let userCoordinates = null
    try {
      const currentLocation = await getCurrentPosition(coordinates)
      userCoordinates = currentLocation.coords
    } catch (e) {
      // do nothing
    }
    getRecommendationsFromAPI(
      userCoordinates,
      dispatch,
      readRecommendations,
      offersSentInLastCall,
      handleFail,
      handleSuccess
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
  resetRecommendations: () => {
    dispatch(assignData({ recommendations: [] }))
  },
})

export default compose(
  withRequiredLogin,
  connect(
    mapStateToProps,
    mapDispatchToProps
  ),
  withGeolocationTracking
)(Discovery)
