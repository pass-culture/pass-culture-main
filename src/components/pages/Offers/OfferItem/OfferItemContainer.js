import { compose } from 'redux'
import { connect } from 'react-redux'

import OfferItem from './OfferItem'
import { selectStocksByOfferId } from 'store/selectors/data/stocksSelectors'
import { selectVenueById } from 'store/selectors/data/venuesSelectors'
import withTracking from '../../../hocs/withTracking'
import { API_URL } from '../../../../utils/config'

export const mapStateToProps = (state, ownProps) => {
  const { offer } = ownProps
  const { id: offerId, venueId } = offer
  const venue = selectVenueById(state, venueId)

  return {
    stocks: selectStocksByOfferId(state, offerId),
    venue,
  }
}

export const mergeProps = (stateProps, dispatchProps, ownProps) => {
  return {
    ...stateProps,
    ...dispatchProps,
    ...ownProps,
    trackActivateOffer: offerId => {
      ownProps.tracking.trackEvent({ action: 'activateOffer', name: offerId })
    },
    trackDeactivateOffer: offerId => {
      ownProps.tracking.trackEvent({ action: 'deactivateOffer', name: offerId })
    },
    updateOffersIsActiveStatus: (id, isActive) =>
      fetch(`${API_URL}/offers/active-status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ offersId: [id], offersActiveStatus: isActive }),
        credentials: 'include',
      }),
  }
}

export default compose(
  withTracking('OfferItem'),
  connect(mapStateToProps, null, mergeProps)
)(OfferItem)
