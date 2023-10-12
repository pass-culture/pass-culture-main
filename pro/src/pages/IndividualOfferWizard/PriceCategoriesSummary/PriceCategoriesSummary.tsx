import React from 'react'

import { useOfferBookingsCount } from 'components/IndividualOfferBreadcrumb/useOfferBookingsCount'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import useOfferWizardMode from 'hooks/useOfferWizardMode'
import IndivualOfferLayout from 'screens/IndividualOffer/IndivualOfferLayout/IndivualOfferLayout'
import { PriceCategoriesSection } from 'screens/IndividualOffer/SummaryScreen/PriceCategoriesSection/PriceCategoriesSection'
import Spinner from 'ui-kit/Spinner/Spinner'

export const PriceCategoriesSummary = (): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const { offer, subCategories, setOffer } = useIndividualOfferContext()
  const { bookingsCount, isLoading } = useOfferBookingsCount(mode, offer?.id)

  if (offer === null || isLoading) {
    return <Spinner />
  }

  const canBeDuo = subCategories.find(
    subCategory => subCategory.id === offer.subcategoryId
  )?.canBeDuo

  return (
    <IndivualOfferLayout
      title="Récapitulatif"
      offer={offer}
      setOffer={setOffer}
      mode={mode}
      bookingsCount={bookingsCount}
    >
      <PriceCategoriesSection offer={offer} canBeDuo={canBeDuo} />
    </IndivualOfferLayout>
  )
}
