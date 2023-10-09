import React from 'react'

import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import useOfferWizardMode from 'hooks/useOfferWizardMode'
import IndividualOfferLayout from 'screens/IndividualOffer/IndividualOfferLayout/IndividualOfferLayout'
import { PriceCategoriesSection } from 'screens/IndividualOffer/SummaryScreen/PriceCategoriesSection/PriceCategoriesSection'
import Spinner from 'ui-kit/Spinner/Spinner'

export const PriceCategoriesSummary = (): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const { offer, subCategories, setOffer } = useIndividualOfferContext()

  if (offer === null) {
    return <Spinner />
  }

  const canBeDuo = subCategories.find(
    subCategory => subCategory.id === offer.subcategoryId
  )?.canBeDuo

  return (
    <IndividualOfferLayout
      title="Récapitulatif"
      offer={offer}
      setOffer={setOffer}
      mode={mode}
    >
      <PriceCategoriesSection offer={offer} canBeDuo={canBeDuo} />
    </IndividualOfferLayout>
  )
}
