/*
* @debt standard "Gaël: prefer useSelector hook vs connect for redux (https://react-redux.js.org/api/hooks)"
*/

import { connect } from 'react-redux'
import { compose } from 'redux'

import withTracking from 'components/hocs/withTracking'
import { showNotification } from 'store/reducers/notificationReducer'

import ActionsBar from './ActionsBar'

export const mapStateToProps = state => {
  return {
    searchFilters: state.offers.searchFilters,
  }
}

export const mapDispatchToProps = dispatch => {
  return {
    showSuccessNotification: text =>
      dispatch(
        showNotification({
          type: 'success',
          text,
        })
      ),
    showPendingNotification: text =>
      dispatch(
        showNotification({
          type: 'pending',
          text,
        })
      ),
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
