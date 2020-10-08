import { connect } from 'react-redux'

import LocalProviderInformation from './LocalProviderInformation'
import { getProviderInfo } from './getProviderInfo'
import { selectOfferById } from 'store/selectors/data/offersSelectors'

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
