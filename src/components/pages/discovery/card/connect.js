import moment from 'moment'
import { mergeData, requestData } from 'redux-saga-data'

import currentRecommendationSelector from '../../../../selectors/currentRecommendation'
import nextRecommendationSelector from '../../../../selectors/nextRecommendation'
import previousRecommendationSelector from '../../../../selectors/previousRecommendation'

const noop = () => {}

const getSelectorByCardPosition = position => {
  switch (position) {
    case 'current':
      return currentRecommendationSelector
    case 'previous':
      return previousRecommendationSelector
    case 'next':
      return nextRecommendationSelector
    default:
      return noop
  }
}

export const mapStateToProps = (state, ownProps) => {
  const { mediationId, offerId } = ownProps.match.params
  const recommendationSelector = getSelectorByCardPosition(ownProps.position)
  const recommendation = recommendationSelector(state, offerId, mediationId, ownProps.position)
  return {
    areDetailsVisible: state.card.areDetailsVisible,
    recommendation,
  }
}

export const mapDispatchToProps = dispatch => ({
  handleClickRecommendation: recommendation => {
    const config = {
      apiPath: `recommendations/${recommendation.id}`,
      body: { isClicked: true },
      method: 'PATCH',
      stateKey: 'recommendations',
    }

    dispatch(requestData(config))
  },

  handleReadRecommendation: recommendation => {
    const readRecommendation = {
      dateRead: moment.utc().toISOString(),
      id: recommendation.id,
    }
    dispatch(
      mergeData({
        readRecommendations: [readRecommendation],
      })
    )
  },
})
