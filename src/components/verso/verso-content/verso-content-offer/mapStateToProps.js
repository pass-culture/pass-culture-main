import get from 'lodash.get'
import { selectBookings } from '../../../../selectors/selectBookings'
import selectMusicTypeByCode from './selectors/selectMusicTypeByCode'
import selectMusicSubTypeByCodeAndSubCode from './selectors/selectMusicSubTypeByCodeAndSubCode'
import selectShowTypeByCode from './selectors/selectShowTypeByCode'
import selectShowSubTypeByCodeAndSubCode from './selectors/selectShowSubTypeByCodeAndSubCode'
import { isRecommendationOfferFinished } from '../../../../helpers'
import { selectBookables } from '../../../../selectors/selectBookables'
import currentRecommendationSelector from '../../../../selectors/currentRecommendation/currentRecommendation'

const getOnlineUrl = (recommendation, state) => {
  const stocks = get(recommendation, 'offer.stocks')
  const stockIds = (stocks || []).map(o => o.id)
  const bookings = selectBookings(state)
  const booking = bookings.find(b => stockIds.includes(b.stockId))
  const onlineOfferUrl = get(booking, 'completedUrl')
  return onlineOfferUrl
}

const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const { mediationId, offerId } = match.params
  const recommendation = currentRecommendationSelector(state, offerId, mediationId)

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

  const onlineOfferUrl = getOnlineUrl(recommendation, state)

  return {
    bookables,
    isFinished,
    musicSubType,
    musicType,
    musicTypes: get(state, 'data.musicTypes'),
    onlineOfferUrl,
    recommendation,
    showSubType,
    showType,
    showTypes: get(state, 'data.showTypes'),
  }
}

export default mapStateToProps
