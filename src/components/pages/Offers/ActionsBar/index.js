import { compose } from 'redux'
import { connect } from 'react-redux'

import withTracking from 'components/hocs/withTracking'
import { hideActionsBar } from 'store/reducers/actionsBar'
import { setSelectedOfferIds } from 'store/reducers/offers'

import ActionsBar from './ActionsBar'

export const mapStateToProps = state => {
  return {
    selectedOfferIds: state.offers.selectedOfferIds,
  }
}

export const mapDispatchToProps = dispatch => {
  return {
    hideActionsBar: () => dispatch(hideActionsBar),
    setSelectedOfferIds: selectedOfferIds => dispatch(setSelectedOfferIds(selectedOfferIds)),
  }
}

export const mergeProps = (stateProps, dispatchProps, ownProps) => {
  return {
    ...stateProps,
    ...dispatchProps,
    ...ownProps,
    trackActivateOffers: offerIds => {
      ownProps.tracking.trackEvent({ action: 'activateOffers', names: offerIds })
    },
    trackDeactivateOffers: offerIds => {
      ownProps.tracking.trackEvent({ action: 'deactivateOffers', names: offerIds })
    },
  }
}

export default compose(
  withTracking('OffersActionsBar'),
  connect(mapStateToProps, mapDispatchToProps, mergeProps)
)(ActionsBar)
