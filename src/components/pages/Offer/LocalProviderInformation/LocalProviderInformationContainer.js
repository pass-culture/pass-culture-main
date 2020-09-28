import { connect } from 'react-redux'
import { compose } from 'redux'

import LocalProviderInformation from './LocalProviderInformation'
import { getProviderInfo } from './getProviderInfo'
import withFrenchQueryRouter from '../../../hocs/withFrenchQueryRouter'
import { selectOfferById } from '../../../../selectors/data/offersSelectors'

export const mapStateToProps = (state, ownProps) => {
  const {
    match: {
      params: { offerId },
    },
    isAllocine,
    isLibraires,
    isTitelive,
    isFnac,
    offererId,
  } = ownProps

  const offer = selectOfferById(state, offerId)
  const { name: offerName, venueId, thumbUrl } = offer
  const providerInfo = getProviderInfo(isTitelive, isAllocine, isLibraires, isFnac)

  return {
    offererId,
    offerName,
    providerInfo,
    thumbUrl,
    venueId,
  }
}

export default compose(withFrenchQueryRouter, connect(mapStateToProps))(LocalProviderInformation)
