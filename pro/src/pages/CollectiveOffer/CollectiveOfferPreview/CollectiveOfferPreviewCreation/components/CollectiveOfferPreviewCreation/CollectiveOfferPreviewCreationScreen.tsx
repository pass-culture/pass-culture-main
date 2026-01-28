import { isBefore } from 'date-fns'
import { useState } from 'react'
import { useNavigate } from 'react-router'
import { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import type {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  GetOffererResponseModel,
} from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import {
  GET_COLLECTIVE_OFFER_QUERY_KEY,
  GET_COLLECTIVE_OFFER_TEMPLATE_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import {
  isCollectiveOfferTemplate,
  Mode,
} from '@/commons/core/OfferEducational/types'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { RedirectToBankAccountDialog } from '@/components/RedirectToBankAccountDialog/RedirectToBankAccountDialog'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import { AdagePreviewLayout } from '@/pages/AdageIframe/app/components/OfferInfos/AdagePreviewLayout/AdagePreviewLayout'
import { PreviewHeader } from '@/pages/CollectiveOffer/CollectiveOfferPreview/components/PreviewHeader'

export interface CollectiveOfferSummaryCreationProps {
  offer:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel
  offerer?: GetOffererResponseModel | null
}

export const CollectiveOfferPreviewCreationScreen = ({
  offer,
  offerer,
}: CollectiveOfferSummaryCreationProps) => {
  const snackBar = useSnackBar()
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

        // eslint-disable-next-line @typescript-eslint/no-floating-promises
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
        snackBar.error(
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

      const isNonFreeOffer =
        newOffer.collectiveStock && newOffer.collectiveStock.price > 0

      const shouldDisplayRedirectDialog =
        isNonFreeOffer &&
        offerer &&
        !offerer.hasNonFreeOffer &&
        !offerer.hasValidBankAccount &&
        !offerer.hasPendingBankAccount

      if (shouldDisplayRedirectDialog) {
        setDisplayRedirectDialog(true)
      } else {
        // eslint-disable-next-line @typescript-eslint/no-floating-promises
        navigate(confirmationUrl)
      }
    } catch {
      snackBar.error(
        'Une erreur est survenue lors de la publication de votre offre.'
      )
      return
    }
  }

  return (
    <div>
      <PreviewHeader offer={offer} />
      <AdagePreviewLayout offer={offer} />
      <ActionsBarSticky>
        <ActionsBarSticky.Left>
          <Button
            as="a"
            variant={ButtonVariant.SECONDARY}
            to={backRedirectionUrl}
            label="Retour"
          />
        </ActionsBarSticky.Left>
        <ActionsBarSticky.Right dirtyForm={false} mode={Mode.CREATION}>
          <Button
            as="a"
            to="/offres/collectives"
            variant={ButtonVariant.SECONDARY}
            onClick={() => {
              logEvent(Events.CLICKED_SAVE_DRAFT_AND_EXIT_COLLECTIVE_OFFER, {
                from: location.pathname,
                offerId: offer.id,
                offerType: 'collective',
              })

              snackBar.success('Brouillon sauvegardé dans la liste des offres')
            }}
            label="Sauvegarder le brouillon et quitter"
          />
          <Button onClick={publishOffer} label="Publier l’offre" />
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
