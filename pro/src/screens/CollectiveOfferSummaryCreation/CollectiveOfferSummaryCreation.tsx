import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  GetOffererResponseModel,
} from 'apiClient/v1'
import ActionsBarSticky from 'components/ActionsBarSticky'
import CollectiveOfferSummary from 'components/CollectiveOfferSummary'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import useActiveFeature from 'hooks/useActiveFeature'
import useNotification from 'hooks/useNotification'
import { RedirectToBankAccountDialog } from 'screens/Offers/RedirectToBankAccountDialog'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import publishCollectiveOfferAdapter from './adapters/publishCollectiveOfferAdapter'
import publishCollectiveOfferTemplateAdapter from './adapters/publishCollectiveOfferTemplateAdapter'
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

  const nextRedirectionUrl = offer.isTemplate
    ? `/offre/${offer.id}/collectif/vitrine/creation/apercu`
    : `/offre/${computeURLCollectiveOfferId(
        offer.id,
        offer.isTemplate
      )}/collectif/confirmation`

  const backRedirectionUrl = offer.isTemplate
    ? `/offre/collectif/vitrine/${offer.id}/creation`
    : `/offre/${offer.id}/collectif/visibilite${
        requestId ? `?requete=${requestId}` : ''
      }`

  const publishOffer = async () => {
    if (offer.isTemplate) {
      const response = await publishCollectiveOfferTemplateAdapter(offer.id)
      if (!response.isOk) {
        return notify.error(response.message)
      }
      setOffer(response.payload)
      return navigate(nextRedirectionUrl)
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
      navigate(nextRedirectionUrl)
    }
  }

  return (
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
        {offer.isTemplate ? (
          <ButtonLink
            variant={ButtonVariant.PRIMARY}
            link={{
              to: nextRedirectionUrl,
              isExternal: false,
            }}
          >
            Étape suivante
          </ButtonLink>
        ) : (
          <Button onClick={publishOffer}>Publier l’offre</Button>
        )}
      </ActionsBarSticky>
      {displayRedirectDialog && offerer?.id && (
        <RedirectToBankAccountDialog
          cancelRedirectUrl={nextRedirectionUrl}
          offerId={offerer?.id}
          venueId={offer.venue.id}
        />
      )}
    </div>
  )
}

export default CollectiveOfferSummaryCreation
