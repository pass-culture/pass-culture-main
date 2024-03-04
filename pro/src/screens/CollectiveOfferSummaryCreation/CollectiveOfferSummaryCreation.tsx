import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  GetOffererResponseModel,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'
import ActionsBarSticky from 'components/ActionsBarSticky'
import CollectiveOfferSummary from 'components/CollectiveOfferSummary'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import useActiveFeature from 'hooks/useActiveFeature'
import useNotification from 'hooks/useNotification'
import { RedirectToBankAccountDialog } from 'screens/Offers/RedirectToBankAccountDialog'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './CollectiveOfferSummaryCreation.module.scss'

interface CollectiveOfferSummaryCreationProps {
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

const CollectiveOfferSummaryCreation = ({
  offer,
  setOffer,
  offerer,
}: CollectiveOfferSummaryCreationProps) => {
  const [displayRedirectDialog, setDisplayRedirectDialog] = useState(false)

  const notify = useNotification()
  const navigate = useNavigate()

  const { requete: requestId } = useParams()

  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )

  const confirmationUrl = offer.isTemplate
    ? `/offre/${offer.id}/collectif/vitrine/confirmation`
    : `/offre/${computeURLCollectiveOfferId(
        offer.id,
        offer.isTemplate
      )}/collectif/confirmation`

  const publishOffer = async () => {
    if (offer.isTemplate) {
      try {
        const resultOffer = await api.patchCollectiveOfferTemplatePublication(
          offer.id
        )
        setOffer({ ...resultOffer, isTemplate: true })
        return navigate(confirmationUrl)
      } catch (error) {
        return notify.error(
          'Une erreur est survenue lors de la publication de votre offre.'
        )
      }
    }

    try {
      const resultOffer = await api.patchCollectiveOfferPublication(offer.id)
      setOffer({ ...resultOffer, isTemplate: false })
      const shouldDisplayRedirectDialog =
        isNewBankDetailsJourneyEnabled &&
        resultOffer.isNonFreeOffer &&
        offerer &&
        !offerer.hasNonFreeOffer &&
        !offerer.hasValidBankAccount &&
        !offerer.hasPendingBankAccount

      if (shouldDisplayRedirectDialog) {
        setDisplayRedirectDialog(true)
      } else {
        navigate(confirmationUrl)
      }
    } catch (error) {
      return notify.error(
        'Une erreur est survenue lors de la publication de votre offre.'
      )
    }
  }
  const backRedirectionUrl = offer.isTemplate
    ? `/offre/collectif/vitrine/${offer.id}/creation`
    : `/offre/${offer.id}/collectif/visibilite${
        requestId ? `?requete=${requestId}` : ''
      }`

  return (
    <>
      <div className={styles['summary']}>
        <CollectiveOfferSummary
          offer={offer}
          offerEditLink={`/offre/collectif${
            offer.isTemplate ? '/vitrine' : ''
          }/${offer.id}/creation`}
          stockEditLink={`/offre/${offer.id}/collectif/stocks`}
          visibilityEditLink={`/offre/${offer.id}/collectif/visibilite`}
        />
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
            <Button onClick={publishOffer}>Publier l’offre</Button>{' '}
          </ActionsBarSticky.Right>
        </ActionsBarSticky>
      </div>
      {displayRedirectDialog && offerer?.id && (
        <RedirectToBankAccountDialog
          cancelRedirectUrl={confirmationUrl}
          offerId={offerer?.id}
          venueId={offer.venue.id}
        />
      )}
    </>
  )
}

export default CollectiveOfferSummaryCreation
