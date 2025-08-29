/* istanbul ignore file */

import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { IndividualOfferLayout } from '@/components/IndividualOfferLayout/IndividualOfferLayout'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { PriceCategoriesSection } from '../components/PriceCategoriesSection/PriceCategoriesSection'
import { IndividualOfferSummaryPriceTable } from '../IndividualOfferSummaryPriceTable/IndividualOfferSummaryPriceTable'

const IndividualOfferSummaryPriceCategories = (): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const { offer, subCategories } = useIndividualOfferContext()
  const isNewOfferCreationFlowFeatureActive = useActiveFeature(
    'WIP_ENABLE_NEW_OFFER_CREATION_FLOW'
  )

  if (isNewOfferCreationFlowFeatureActive) {
    return <IndividualOfferSummaryPriceTable />
  }

  if (offer === null) {
    return <Spinner />
  }

  const canBeDuo = subCategories.find(
    (subCategory) => subCategory.id === offer.subcategoryId
  )?.canBeDuo

  return (
    <IndividualOfferLayout title="Récapitulatif" offer={offer} mode={mode}>
      <PriceCategoriesSection
        offer={offer}
        canBeDuo={canBeDuo}
        shouldShowDivider={false}
      />
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferSummaryPriceCategories
