import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { selectCurrentUser } from 'with-react-redux-login'

import ShareButton from './ShareButton'
import { getShareURL } from '../../../helpers'
import { getCurrentRecommendationOfferName } from '../../../selectors/currentRecommendation/getCurrentRecommendationOffername'
import { getShare } from '../../../selectors/shareSelectors'

export const mapStateToProps = (state, ownProps) => {
  const {
    match: {
      params: { mediationId, offerId },
    },
  } = ownProps
  const offerName = getCurrentRecommendationOfferName(state, offerId, mediationId)
  const text = offerName && `Retrouvez ${offerName} sur le pass Culture`
  const user = selectCurrentUser(state)
  const url = (user && getShareURL(user, offerId, mediationId)) || null

  return {
    offerName,
    text,
    url,
    ...getShare(state),
  }
}

export const ShareButtonContainer = compose(
  withRouter,
  connect(mapStateToProps)
)(ShareButton)

export default compose(
  withRouter,
  connect(mapStateToProps)
)(ShareButton)
