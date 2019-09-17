import { connect } from 'react-redux'

import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { selectCurrentUser } from 'with-react-redux-login'
import track from 'react-tracking'

import ShareButton from './ShareButton'
import { getShareURL } from '../../../../helpers'
import { trackEventWrapper } from '../../../../helpers/matomo/trackEventWrapper'
import selectMediationByRouterMatch from '../../../../selectors/selectMediationByRouterMatch'
import selectOfferByRouterMatch from '../../../../selectors/selectOfferByRouterMatch'
import { openSharePopin, closeSharePopin } from '../../../../reducers/share'

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

export const mapDispatchToProps = (dispatch, ownProps) => ({
  openPopin: popinOptions => dispatch(openSharePopin(popinOptions)),
  closePopin: () => dispatch(closeSharePopin()),
  trackShareOfferByMail: offerId => {
    ownProps.tracking.trackEvent({ action: 'shareMail', name: offerId })
  },
  trackShareOfferByLink: offerId => {
    ownProps.tracking.trackEvent({ action: 'shareLink', name: offerId })
  },
})

export const mergeProps = (stateProps, dispatchProps) => {
  const { trackShareOfferByMail, trackShareOfferByLink } = dispatchProps
  const { offerId } = stateProps

  return {
    ...stateProps,
    ...dispatchProps,
    trackShareOfferByMail: () => trackShareOfferByMail(offerId),
    trackShareOfferByLink: () => trackShareOfferByLink(offerId),
  }
}

export default compose(
  withRouter,
  track({ page: 'Offer' }, { dispatch: trackEventWrapper }),
  connect(
    mapStateToProps,
    mapDispatchToProps,
    mergeProps
  )
)(ShareButton)
