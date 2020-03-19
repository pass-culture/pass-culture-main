import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { selectCurrentUser } from '../../../hocs/with-login/with-react-redux-login'

import withTracking from '../../../hocs/withTracking'
import ShareButton from './ShareButton'
import getShareURL from '../../../../utils/getShareURL'
import { selectOfferByRouterMatch } from '../../../../selectors/data/offersSelectors'
import { openSharePopin, closeSharePopin } from '../../../../reducers/share'
import { selectMediationByRouterMatch } from '../../../../selectors/data/mediationsSelectors'

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
  openPopin: popinOptions => dispatch(openSharePopin(popinOptions)),
  closePopin: () => dispatch(closeSharePopin()),
})

export const mergeProps = (stateProps, dispatchProps, ownProps) => {
  const { offerId } = stateProps

  return {
    ...stateProps,
    ...dispatchProps,
    trackShareOfferByMail: () => {
      ownProps.tracking.trackEvent({ action: 'shareMail', name: offerId })
    },
    trackShareOfferByLink: () => {
      ownProps.tracking.trackEvent({ action: 'shareLink', name: offerId })
    },
  }
}

export default compose(
  withRouter,
  withTracking('Offer'),
  connect(
    mapStateToProps,
    mapDispatchToProps,
    mergeProps
  )
)(ShareButton)
