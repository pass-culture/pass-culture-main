import moment from 'moment'
import { mergeData, requestData } from 'pass-culture-shared'

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
  const recomendationSelector = getSelectorByCardPosition(ownProps.position)
  const recommendation = recomendationSelector(
    state,
    offerId,
    mediationId,
    ownProps.position
  )
  return {
    isShownDetails: state.verso.isShownDetails,
    recommendation,
  }
}

export const mapDispatchToProps = dispatch => ({
  handleClickRecommendation: recommendation => {
    const options = {
      body: { isClicked: true },
      key: 'recommendations',
    }

    const path = `recommendations/${recommendation.id}`

    dispatch(requestData('PATCH', path, options))
  },

  handleReadRecommendation: recommendation => {
    const readRecommendation = Object.assign({}, recommendation, {
      dateRead: moment.utc().toISOString(),
    })
    dispatch(mergeData({ readRecommendations: [readRecommendation] }))
  },
})
