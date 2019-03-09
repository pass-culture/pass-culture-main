import get from 'lodash.get'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import currentRecommendationSelector from '../../selectors/currentRecommendation'
import { getShareURL } from '../../helpers'
import ShareButtonContent from './ShareButtonContent'

const mapStateToProps = (state, ownProps) => {
  const { user } = state
  const { location } = ownProps
  const { mediationId, offerId } = ownProps.match.params
  const recommendation = currentRecommendationSelector(
    state,
    offerId,
    mediationId
  )
  const url = (user && getShareURL(location, user)) || null
  const offerName = get(recommendation, 'offer.eventOrThing.name')
  const text = offerName && `Retrouvez ${offerName} sur le pass Culture`
  return { offerName, text, url, ...state.share }
}

export const ShareButton = compose(
  withRouter,
  connect(mapStateToProps)
)(ShareButtonContent)

export default ShareButton
