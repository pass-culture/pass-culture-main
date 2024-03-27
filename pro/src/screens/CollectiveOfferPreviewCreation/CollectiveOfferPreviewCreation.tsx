import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  GetOffererResponseModel,
} from 'apiClient/v1'
import ActionsBarSticky from 'components/ActionsBarSticky'
import useActiveFeature from 'hooks/useActiveFeature'
import useNotification from 'hooks/useNotification'
import AdagePreviewLayout from 'pages/AdageIframe/app/components/OfferInfos/AdagePreviewLayout/AdagePreviewLayout'
import publishCollectiveOfferAdapter from 'screens/CollectiveOfferSummaryCreation/adapters/publishCollectiveOfferAdapter'
import publishCollectiveOfferTemplateAdapter from 'screens/CollectiveOfferSummaryCreation/adapters/publishCollectiveOfferTemplateAdapter'
import { RedirectToBankAccountDialog } from 'screens/Offers/RedirectToBankAccountDialog'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

export interface CollectiveOfferSummaryCreationProps {
  offer:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel
  setOffer: (
    offer:
      | GetCollectiveOfferResponseModel
      | GetCollectiveOfferTemplateResponseModel
  ) => void
  offerer: GetOffererResponseModel | undefined
}

const CollectiveOfferPreviewCreationScreen = ({
  offer,
  setOffer,
  offerer,
}: CollectiveOfferSummaryCreationProps) => {
  const notify = useNotification()
  const navigate = useNavigate()
  const [displayRedirectDialog, setDisplayRedirectDialog] = useState(false)
  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )

  const backRedirectionUrl = offer.isTemplate
    ? `/offre/${offer.id}/collectif/vitrine/creation/recapitulatif`
    : `/offre/${offer.id}/collectif/creation/recapitulatif`

  const confirmationUrl = offer.isTemplate
    ? `/offre/${offer.id}/collectif/vitrine/confirmation`
    : `/offre/${offer.id}/collectif/confirmation`

  const publishOffer = async () => {
    if (offer.isTemplate) {
      const response = await publishCollectiveOfferTemplateAdapter(offer.id)

      if (!response.isOk) {
        notify.error(response.message)
        return
      }

      setOffer(response.payload)
      navigate(confirmationUrl)
    }

    const response = await publishCollectiveOfferAdapter(offer.id)
    if (!response.isOk) {
      return notify.error(response.message)
    }
    setOffer(response.payload)
    const shouldDisplayRedirectDialog =
      isNewBankDetailsJourneyEnabled &&
      response.payload.isNonFreeOffer &&
      offerer &&
      !offerer.hasNonFreeOffer &&
      !offerer.hasValidBankAccount &&
      !offerer.hasPendingBankAccount

    if (shouldDisplayRedirectDialog) {
      setDisplayRedirectDialog(true)
    } else {
      navigate(confirmationUrl)
    }
  }

  return (
    <div>
      <p>
        Voici à quoi ressemblera votre offre une fois publiée sur la plateforme
        ADAGE.
      </p>
      <AdagePreviewLayout offer={offer} />
      <ActionsBarSticky>
        <ActionsBarSticky.Left>
          <ButtonLink
            variant={ButtonVariant.SECONDARY}
            link={{
              to: backRedirectionUrl,
              isExternal: false,
            }}
          >
            Étape précédente
          </ButtonLink>
        </ActionsBarSticky.Left>
        <ActionsBarSticky.Right>
          <Button onClick={publishOffer}>Publier l’offre</Button>
        </ActionsBarSticky.Right>
      </ActionsBarSticky>
      {displayRedirectDialog && offerer?.id && (
        <RedirectToBankAccountDialog
          cancelRedirectUrl={confirmationUrl}
          offerId={offerer.id}
          venueId={offer.venue.id}
        />
      )}
    </div>
  )
}

export default CollectiveOfferPreviewCreationScreen
