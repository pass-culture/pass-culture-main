import React from 'react'

import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import useOfferWizardMode from 'hooks/useOfferWizardMode'
import IndividualOfferLayout from 'screens/IndividualOffer/IndividualOfferLayout/IndividualOfferLayout'
import { getTitle } from 'screens/IndividualOffer/IndividualOfferLayout/utils/getTitle'
import { PriceCategoriesScreen } from 'screens/IndividualOffer/PriceCategoriesScreen/PriceCategoriesScreen'
import Spinner from 'ui-kit/Spinner/Spinner'

export const PriceCategories = (): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const { offer, setOffer } = useIndividualOfferContext()

  // Offer might be null: when we submit Informations form, we setOffer with the
  // submited payload. Due to React 18 render batching behavior and react-router
  // implementation, this component can be rendered before the offer is set in the
  // offer individual context
  if (offer === null) {
    return <Spinner />
  }

  return (
    <IndividualOfferLayout
      offer={offer}
      setOffer={setOffer}
      title={getTitle(mode)}
      mode={mode}
    >
      <PriceCategoriesScreen offer={offer} />
    </IndividualOfferLayout>
  )
}
