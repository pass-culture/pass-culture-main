import React from 'react'

import { queryParamsFromOfferer } from 'components/pages/Offers/utils/queryParamsFromOfferer'
import { canOffererCreateEducationalOffer } from 'repository/pcapi/pcapi'
import OfferTypeScreen from 'screens/OfferType'

const OfferType = (): JSX.Element => {
  const { structure } = queryParamsFromOfferer(location)

  const fetchCanOffererCreateEducationalOffer = () =>
    canOffererCreateEducationalOffer(structure)

  return (
    <OfferTypeScreen
      fetchCanOffererCreateEducationalOffer={
        fetchCanOffererCreateEducationalOffer
      }
    />
  )
}

export default OfferType
