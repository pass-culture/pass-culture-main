import { connect } from 'react-redux'
import { compose } from 'redux'

import selectOfferById from '../../../../selectors/selectOfferById'
import TiteLiveInformation from './TiteLiveInformation'
import withFrenchQueryRouter from '../../../hocs/withFrenchQueryRouter'
import {getProductById} from '../../../../selectors/data/productsSelectors'

export const mapStateToProps = (state, ownProps) => {
  const {
    match: {
      params: { offerId },
    },
    offererId,
  } = ownProps

  const offer = selectOfferById(state, offerId)
  const product = getProductById(state, offer.productId)
  const { venueId } = offer
  const { name: offerName } = offer
  const { thumbUrl } = product

  return {
    offererId,
    offerName,
    thumbUrl,
    venueId,
  }
}

export default compose(
  withFrenchQueryRouter,
  connect(mapStateToProps)
)(TiteLiveInformation)
