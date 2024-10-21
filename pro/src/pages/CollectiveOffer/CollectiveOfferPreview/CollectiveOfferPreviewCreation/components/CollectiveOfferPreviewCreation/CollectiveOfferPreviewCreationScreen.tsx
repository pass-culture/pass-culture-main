import { isBefore } from 'date-fns'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  GetOffererResponseModel,
} from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import {
  GET_COLLECTIVE_OFFER_QUERY_KEY,
  GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY,
} from 'commons/config/swrQueryKeys'
import { Events } from 'commons/core/FirebaseEvents/constants'
import {
  Mode,
  isCollectiveOfferTemplate,
} from 'commons/core/OfferEducational/types'
import { useNotification } from 'commons/hooks/useNotification'
import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import { AdagePreviewLayout } from 'pages/AdageIframe/app/components/OfferInfos/AdagePreviewLayout/AdagePreviewLayout'
import { RedirectToBankAccountDialog } from 'pages/Offers/components/IndividualOffersScreen/RedirectToBankAccountDialog'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

export interface CollectiveOfferSummaryCreationProps {
  offer:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel
  offerer: GetOffererResponseModel | undefined
}

export const CollectiveOfferPreviewCreationScreen = ({
  offer,
  offerer,
}: CollectiveOfferSummaryCreationProps) => {
  const notify = useNotification()
  const navigate = useNavigate()
  const { mutate } = useSWRConfig()
  const { logEvent } = useAnalytics()
  const [displayRedirectDialog, setDisplayRedirectDialog] = useState(false)

  const backRedirectionUrl = offer.isTemplate
    ? `/offre/${offer.id}/collectif/vitrine/creation/recapitulatif`
    : `/offre/${offer.id}/collectif/creation/recapitulatif`

  const confirmationUrl = offer.isTemplate
    ? `/offre/${offer.id}/collectif/vitrine/confirmation`
    : `/offre/${offer.id}/collectif/confirmation`

  const publishOffer = async () => {
    try {
      if (isCollectiveOfferTemplate(offer)) {
        const newOffer = await api.patchCollectiveOfferTemplatePublication(
          offer.id
        )

        await mutate<GetCollectiveOfferTemplateResponseModel>(
          [GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY, offer.id],
          newOffer,
          { revalidate: false }
        )

        navigate(confirmationUrl)
        return
      }

      //  This is temporary, the api should return an error with a specific message type
      //  Until then, we have to manually verify that the dates of the offer are not in the past,
      //  Which can happen for a draft offer that is published after some time
      const areOfferDatesInvalid =
        (offer.collectiveStock?.bookingLimitDatetime &&
          isBefore(
            new Date(offer.collectiveStock.bookingLimitDatetime),
            new Date()
          )) ||
        (offer.collectiveStock?.startDatetime &&
          isBefore(new Date(offer.collectiveStock.startDatetime), new Date()))
      if (areOfferDatesInvalid) {
        notify.error(
          'Les dates de limite de réservation ou d’évènement doivent être égales ou postérieures à la date actuelle.'
        )
        return
      }

      const newOffer = await api.patchCollectiveOfferPublication(offer.id)

      await mutate<GetCollectiveOfferResponseModel>(
        [GET_COLLECTIVE_OFFER_QUERY_KEY, offer.id],
        newOffer,
        { revalidate: false }
      )

      const shouldDisplayRedirectDialog =
        newOffer.isNonFreeOffer &&
        offerer &&
        !offerer.hasNonFreeOffer &&
        !offerer.hasValidBankAccount &&
        !offerer.hasPendingBankAccount

      if (shouldDisplayRedirectDialog) {
        setDisplayRedirectDialog(true)
      } else {
        navigate(confirmationUrl)
      }
    } catch {
      notify.error(
        'Une erreur est survenue lors de la publication de votre offre.'
      )
      return
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
          <ButtonLink variant={ButtonVariant.SECONDARY} to={backRedirectionUrl}>
            Retour
          </ButtonLink>
        </ActionsBarSticky.Left>
        <ActionsBarSticky.Right dirtyForm={false} mode={Mode.CREATION}>
          <ButtonLink
            to="/offres/collectives"
            variant={ButtonVariant.SECONDARY}
            onClick={() => {
              logEvent(Events.CLICKED_SAVE_DRAFT_AND_EXIT_COLLECTIVE_OFFER, {
                from: location.pathname,
              })

              notify.success('Brouillon sauvegardé dans la liste des offres')
            }}
          >
            Sauvegarder le brouillon et quitter
          </ButtonLink>
          <Button onClick={publishOffer}>Publier l’offre</Button>
        </ActionsBarSticky.Right>
      </ActionsBarSticky>
      {offerer?.id && (
        <RedirectToBankAccountDialog
          cancelRedirectUrl={confirmationUrl}
          offerId={offerer.id}
          venueId={offer.venue.id}
          isDialogOpen={displayRedirectDialog}
        />
      )}
    </div>
  )
}
