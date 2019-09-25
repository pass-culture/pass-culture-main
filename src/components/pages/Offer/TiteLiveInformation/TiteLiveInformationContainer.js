import { connect } from 'react-redux'
import { compose } from 'redux'
import get from 'lodash.get'

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
  const venueId = get(offer, 'venueId')

  if (!offer) {
    return {}
  }

  const thumbUrl = get(product, 'thumbUrl')

  return {
    offererId,
    thumbUrl,
    venueId,
  }
}

export default compose(
  withFrenchQueryRouter,
  connect(mapStateToProps)
)(TiteLiveInformation)
