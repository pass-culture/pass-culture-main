import React from 'react'
import { useLocation } from 'react-router'

import { queryParamsFromOfferer } from 'components/pages/Offers/utils/queryParamsFromOfferer'
import OfferEducationalConfirmationScreen from 'screens/OfferEducationalConfirmation'

const OfferEducationalConfirmation = (): JSX.Element => {
  const location = useLocation<{ structure?: string; lieu?: string }>()

  const { structure: offererId, lieu: venueId } =
    queryParamsFromOfferer(location)

  return (
    <OfferEducationalConfirmationScreen
      offererId={offererId}
      venueId={venueId}
    />
  )
}

export default OfferEducationalConfirmation
