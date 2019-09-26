import { connect } from 'react-redux'
import { compose } from 'redux'

import selectOfferById from '../../../../selectors/selectOfferById'
import TiteLiveInformation from './TiteLiveInformation'
import withFrenchQueryRouter from '../../../hocs/withFrenchQueryRouter'

export const mapStateToProps = (state, ownProps) => {
  const {
    match: {
      params: { offerId },
    },
    offererId,
    product,
  } = ownProps

  const offer = selectOfferById(state, offerId)
  const { venueId } = offer
  const { name: productName, thumbUrl } = product

  return {
    offererId,
    productName,
    thumbUrl,
    venueId,
  }
}

export default compose(
  withFrenchQueryRouter,
  connect(mapStateToProps)
)(TiteLiveInformation)
