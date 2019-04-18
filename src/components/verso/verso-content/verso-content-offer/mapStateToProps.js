import get from 'lodash.get'
import selectMusicTypeByCode from './selectors/selectMusicTypeByCode'
import selectMusicSubTypeByCodeAndSubCode from './selectors/selectMusicSubTypeByCodeAndSubCode'
import selectShowTypeByCode from './selectors/selectShowTypeByCode'
import selectShowSubTypeByCodeAndSubCode from './selectors/selectShowSubTypeByCodeAndSubCode'
import { isRecommendationOfferFinished } from '../../../../helpers'
import { selectBookables } from '../../../../selectors/selectBookables'
import currentRecommendationSelector from '../../../../selectors/currentRecommendation'


const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const { mediationId, offerId } = match.params
  const recommendation = currentRecommendationSelector(
    state,
    offerId,
    mediationId
  )

  const bookables = selectBookables(state, recommendation, match)
  const isFinished = isRecommendationOfferFinished(recommendation, offerId)

  const extraData = get(recommendation, 'offer.eventOrThing.extraData')
  const musicType = selectMusicTypeByCode(state, get(extraData, 'musicType'))
  const showType = selectShowTypeByCode(state, get(extraData, 'showType'))
  const musicSubType = selectMusicSubTypeByCodeAndSubCode(
    state,
    get(extraData, 'musicType'),
    get(extraData, 'musicSubType')
  )
  const showSubType = selectShowSubTypeByCodeAndSubCode(
    state,
    get(extraData, 'showType'),
    get(extraData, 'showSubType')
  )

  return {
    bookables,
    isFinished,
    musicSubType,
    musicType,
    musicTypes: get(state, 'data.musicTypes'),
    recommendation,
    showSubType,
    showType,
    showTypes: get(state, 'data.showTypes'),
  }
}

export default mapStateToProps
