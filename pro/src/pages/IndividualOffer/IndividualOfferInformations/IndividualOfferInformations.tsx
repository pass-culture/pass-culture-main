import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { IndividualOfferLayout } from '@/components/IndividualOfferLayout/IndividualOfferLayout'
import { getTitle } from '@/components/IndividualOfferLayout/utils/getTitle'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { IndividualOfferLocation } from '../IndividualOfferLocation/IndividualOfferLocation'
import { IndividualOfferInformationsScreen } from './components/IndividualOfferInformationsScreen'

// TODO (igabriele, 2025-08-14): Replace this page with `<IndividualOfferLocation />` once `WIP_ENABLE_NEW_OFFER_CREATION_FLOW` FF is enabled in production.
const IndividualOfferInformations = (): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const { offer, publishedOfferWithSameEAN } = useIndividualOfferContext()
  const isNewOfferCreationFlowFeatureActive = useActiveFeature(
    'WIP_ENABLE_NEW_OFFER_CREATION_FLOW'
  )

  if (isNewOfferCreationFlowFeatureActive) {
    return <IndividualOfferLocation />
  }

  if (!offer) {
    return <Spinner />
  }

  return (
    <IndividualOfferLayout
      offer={offer}
      title={getTitle(mode)}
      mode={mode}
      venueHasPublishedOfferWithSameEan={Boolean(publishedOfferWithSameEAN)}
    >
      <IndividualOfferInformationsScreen offer={offer} />
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferInformations
