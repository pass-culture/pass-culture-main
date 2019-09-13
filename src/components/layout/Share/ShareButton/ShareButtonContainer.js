import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { selectCurrentUser } from 'with-react-redux-login'

import ShareButton from './ShareButton'
import selectMediationByRouterMatch from '../../../../selectors/selectMediationByRouterMatch'
import selectOfferByRouterMatch from '../../../../selectors/selectOfferByRouterMatch'
import { openSharePopin, closeSharePopin } from '../../../../reducers/share'
import { getShareURL } from '../../../../helpers'

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
    offerId,
    ...state.share,
  }
}

export const mapDispatchToProps = dispatch => ({
  openPopin: popinOptions => {
    dispatch(openSharePopin(popinOptions))
  },
  closePopin: () => {
    dispatch(closeSharePopin())
  },
})

export default compose(
  withRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(ShareButton)
