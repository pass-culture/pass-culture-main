import get from 'lodash.get'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { selectCurrentUser } from 'with-react-redux-login'

import ShareButton from './ShareButton'
import { getShareURL } from '../../../helpers'
import currentRecommendationSelector from '../../../selectors/currentRecommendation'

export const mapStateToProps = (state, ownProps) => {
  const { location } = ownProps
  const { mediationId, offerId } = ownProps.match.params
  const recommendation = currentRecommendationSelector(state, offerId, mediationId)
  const user = selectCurrentUser(state)
  const url = (user && getShareURL(location, user)) || null
  const offerName = get(recommendation, 'offer.name')
  const text = offerName && `Retrouvez ${offerName} sur le pass Culture`
  return { offerName, text, url, ...state.share }
}

export const ShareButtonContainer = compose(
  withRouter,
  connect(mapStateToProps)
)(ShareButton)

export default ShareButtonContainer
