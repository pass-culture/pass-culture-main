import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { IndividualOfferLayout } from '@/components/IndividualOfferLayout/IndividualOfferLayout'
import { getTitle } from '@/components/IndividualOfferLayout/utils/getTitle'
import { IndividualOfferPriceTable } from '@/pages/IndividualOffer/IndividualOfferPriceTable/IndividualOfferPriceTable'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { IndividualOfferPriceCategoriesScreen } from './components/IndividualOfferPriceCategoriesScreen'

export const IndividualOfferPriceCategories = (): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const { offer } = useIndividualOfferContext()
  const isNewOfferCreationFlowFeatureActive = useActiveFeature(
    'WIP_ENABLE_NEW_OFFER_CREATION_FLOW'
  )

  if (isNewOfferCreationFlowFeatureActive) {
    return <IndividualOfferPriceTable />
  }

  // Offer might be null: when we submit Informations form, we setOffer with the
  // submited payload. Due to React 18 render batching behavior and react-router
  // implementation, this component can be rendered before the offer is set in the
  // offer individual context
  if (offer === null) {
    return <Spinner />
  }

  return (
    <IndividualOfferLayout offer={offer} title={getTitle(mode)} mode={mode}>
      <IndividualOfferPriceCategoriesScreen offer={offer} />
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferPriceCategories
