import { compose } from 'redux'
import { connect } from 'react-redux'
import { requestData } from 'redux-saga-data'

import OfferItem from './OfferItem'
import { selectStocksByOfferId } from 'store/selectors/data/stocksSelectors'
import { selectVenueById } from 'store/selectors/data/venuesSelectors'
import { offerNormalizer } from '../../../../utils/normalizers'
import withTracking from '../../../hocs/withTracking'
import { API_URL } from '../../../../utils/config'

export const mapDispatchToProps = dispatch => ({
  activateOffer: id =>
    fetch(`${API_URL}/offers/activate`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ offersId: [id] }),
      credentials: 'include',
    }),
  deactivateOffer: id => {
    dispatch(
      requestData({
        apiPath: `/offers/${id}`,
        body: {
          isActive: false,
        },
        isMergingDatum: true,
        isMutatingDatum: true,
        isMutaginArray: false,
        method: 'PATCH',
        normalizer: offerNormalizer,
      })
    )
  },
})

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
  }
}

export default compose(
  withTracking('OfferItem'),
  connect(mapStateToProps, mapDispatchToProps, mergeProps)
)(OfferItem)
