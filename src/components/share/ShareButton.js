import { compose } from 'redux'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'

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
  const title =
    (recommendation && recommendation.offer.eventOrThing.name) || null
  return { title, url }
}

export const ShareButton = compose(
  withRouter,
  connect(mapStateToProps)
)(ShareButtonContent)

export default ShareButton
