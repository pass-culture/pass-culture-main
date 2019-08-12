import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { selectCurrentUser } from 'with-react-redux-login'

import ShareButton from './ShareButton'
import { getShareURL } from '../../../../helpers'
import selectMediationByRouterMatch from '../../../../selectors/selectMediationByRouterMatch'
import selectOfferByRouterMatch from '../../../../selectors/selectOfferByRouterMatch'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const mediation = selectMediationByRouterMatch(state, match)
  const { id: mediationId } = mediation || {}
  const offer = selectOfferByRouterMatch(state, match)
  const { id: offerId, name: offerName } = offer || {}
  const text = offerName && `Retrouvez ${offerName} sur le pass Culture`
  const user = selectCurrentUser(state)
  const url = getShareURL(user, offerId, mediationId)

  return {
    offerName,
    text,
    url,
    ...state.share,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(ShareButton)
