import { lastTrackerMoment } from 'pass-culture-shared'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { assignData, requestData } from 'redux-saga-data'

import Offers from './Offers'
import { withRequiredLogin } from '../../hocs'
import selectOffererById from '../../../selectors/selectOffererById'
import selectOffersByOffererIdAndVenueId from '../../../selectors/selectOffersByOffererIdAndVenueId'
import selectVenueById from '../../../selectors/selectVenueById'
import { offerNormalizer } from '../../../utils/normalizers'
import { translateQueryParamsToApiParams } from '../../../utils/translate'

export const mapStateToProps = (state, ownProps) => {
  const { query } = ownProps
  const queryParams = query.parse()
  const apiQueryParams = translateQueryParamsToApiParams(queryParams)
  const { offererId, venueId } = apiQueryParams

  return {
    lastTrackerMoment: lastTrackerMoment(state, 'offers'),
    offers: selectOffersByOffererIdAndVenueId(state, offererId, venueId),
    offerer: selectOffererById(state, offererId),
    types: state.data.types,
    venue: selectVenueById(state, venueId),
  }
}

export const mapDispatchToProps = dispatch => ({
  dispatch,

  loadOffers: config =>
    dispatch(
      requestData({
        ...config,
        normalizer: offerNormalizer,
      })
    ),

  resetLoadedOffers: () => dispatch(assignData({ offers: [] })),
})

export default compose(
  withRequiredLogin,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(Offers)
