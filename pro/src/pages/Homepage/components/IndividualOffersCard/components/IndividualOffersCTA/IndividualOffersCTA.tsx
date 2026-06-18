import { OfferStatus } from '@/apiClient/v1'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'

type IndividualOffersCTAProps = {
  offerStatus: OfferStatus
  offerId: number
}

export const IndividualOffersCTA = ({
  offerStatus,
  offerId,
}: IndividualOffersCTAProps): JSX.Element => {
  const isOfferExposureEnabled = useActiveFeature('WIP_OFFER_EXPOSURE')

  if (offerStatus === OfferStatus.SOLD_OUT) {
    const offerLink = getIndividualOfferUrl({
      offerId,
      mode: OFFER_WIZARD_MODE.EDITION,
      step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
    })
    return (
      <Button
        variant={ButtonVariant.SECONDARY}
        label="Ajouter du stock"
        as="a"
        to={offerLink}
      />
    )
  }

  const offerLink = getIndividualOfferUrl({
    offerId,
    mode: OFFER_WIZARD_MODE.READ_ONLY,
    step: isOfferExposureEnabled
      ? INDIVIDUAL_OFFER_WIZARD_STEP_IDS.EXPOSURE
      : INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION,
    isOfferExposureEnabled,
  })

  return (
    <Button
      variant={ButtonVariant.SECONDARY}
      label="Voir l'offre"
      as="a"
      to={offerLink}
    />
  )
}
