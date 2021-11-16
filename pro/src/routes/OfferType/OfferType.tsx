import React from 'react'
import { useLocation } from 'react-router'

import { queryParamsFromOfferer } from 'components/pages/Offers/utils/queryParamsFromOfferer'
import { canOffererCreateEducationalOffer } from 'repository/pcapi/pcapi'
import OfferTypeScreen from 'screens/OfferType'

const OfferType = (): JSX.Element => {
  const location = useLocation()

  const { structure } = queryParamsFromOfferer(location)
  
  const fetchCanOffererCreateEducationalOffer = () => canOffererCreateEducationalOffer(structure)

  return (
    <OfferTypeScreen fetchCanOffererCreateEducationalOffer={fetchCanOffererCreateEducationalOffer} />
  )
}

export default OfferType
