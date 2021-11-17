import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import { requestData } from '../../../utils/fetch-normalize-data/requestData'
import isCancelView from '../../../utils/isCancelView'
import { offerNormalizer } from '../../../utils/normalizers'
import Details from './Details'
import selectIsFeatureDisabled from '../../router/selectors/selectIsFeatureDisabled'
import { FEATURES } from '../../router/selectors/features'
import withTracking from '../../hocs/withTracking'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const cancelView = isCancelView(match)
  const webAppV2Enabled = !selectIsFeatureDisabled(state, FEATURES.WEBAPP_V2_ENABLED)
  return {
    webAppV2Enabled,
    cancelView,
  }
}

export const mapDispatchToProps = dispatch => ({
  getOfferById: offerId => {
    dispatch(
      requestData({
        apiPath: `/offers/${offerId}`,
        normalizer: offerNormalizer,
      })
    )
  },
})


export const mergeProps = (stateProps, dispatchProps, ownProps) => {
  return {
    ...stateProps,
    ...dispatchProps,
    ...ownProps,
    trackV1toV2HomeRedirect: ({ url, offerId }) => {
      ownProps.tracking.trackEvent({
        action: 'OfferDetailsContainer_V1toV2HomeRedirect',
        name: `Redirect: ${url} - Offer id: ${offerId}`,
      })
    },
    trackV1toV2OfferRedirect: ({ url, offerId }) => {
      ownProps.tracking.trackEvent({
        action: 'OfferDetailsContainer_V1toV2OfferRedirect',
        name: `Redirect: ${url} - Offer id: ${offerId}`,
      })
    },
  }
}

export default compose(
  withTracking('OfferDetailsContainer'),
  withRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps,
    mergeProps
  )
)(Details)
