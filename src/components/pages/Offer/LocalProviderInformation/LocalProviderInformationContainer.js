import { connect } from 'react-redux'

import { selectOfferById } from 'store/offers/selectors'

import { getProviderInfo } from './getProviderInfo'
import LocalProviderInformation from './LocalProviderInformation'

export const mapStateToProps = (state, ownProps) => {
  const { offerId, providerName, offererId } = ownProps

  const offer = selectOfferById(state, offerId)
  const { name: offerName, venueId, thumbUrl } = offer
  const providerInfo = getProviderInfo(providerName)

  return {
    offererId,
    offerName,
    providerInfo,
    thumbUrl,
    venueId,
  }
}

export default connect(mapStateToProps)(LocalProviderInformation)
