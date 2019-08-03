import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { selectCurrentUser } from 'with-react-redux-login'

import ShareButton from './ShareButton'
import { getShareURL } from '../../../../helpers'
import selectMediationByMatch from '../../../../selectors/selectMediationByMatch'
import selectOfferByMatch from '../../../../selectors/selectOfferByMatch'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const mediation = selectMediationByMatch(state, match)
  const { id: mediationId } = mediation || {}
  const offer = selectOfferByMatch(state, match)
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
