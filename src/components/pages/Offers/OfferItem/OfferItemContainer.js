import { compose } from 'redux'
import { connect } from 'react-redux'
import { requestData } from 'redux-saga-data'
import { withRouter } from 'react-router'

import OfferItem from './OfferItem'
import { selectStocksByOfferId } from '../../../../selectors/data/stocksSelectors'
import { selectVenueById } from '../../../../selectors/data/venuesSelectors'
import { offerNormalizer } from '../../../../utils/normalizers'
import withTracking from '../../../hocs/withTracking'

export const mapDispatchToProps = dispatch => ({
  updateOffer: (id, status) => {
    dispatch(
      requestData({
        apiPath: `/offers/${id}`,
        body: {
          isActive: status,
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
  withRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps,
    mergeProps
  )
)(OfferItem)
