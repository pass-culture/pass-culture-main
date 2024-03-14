import React from 'react'
import { useNavigate } from 'react-router-dom'

import {
  GetCollectiveOfferTemplateResponseModel,
  GetCollectiveOfferResponseModel,
} from 'apiClient/v1'
import ActionsBarSticky from 'components/ActionsBarSticky'
import CollectiveOfferSummary from 'components/CollectiveOfferSummary'
import OfferEducationalActions from 'components/OfferEducationalActions'
import {
  Events,
  OFFER_FROM_TEMPLATE_ENTRIES,
} from 'core/FirebaseEvents/constants'
import {
  createOfferFromTemplate,
  isCollectiveOfferTemplate,
  Mode,
} from 'core/OfferEducational'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import { computeCollectiveOffersUrl } from 'core/Offers/utils'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import fullEditIcon from 'icons/full-edit.svg'
import fullMoreIcon from 'icons/full-more.svg'
import fullShowIcon from 'icons/full-show.svg'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './CollectiveOfferSummaryEdition.module.scss'

interface CollectiveOfferSummaryEditionProps {
  offer:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel
  reloadCollectiveOffer: () => void
  mode: Mode
}

const CollectiveOfferSummaryEdition = ({
  offer,
  reloadCollectiveOffer,
  mode,
}: CollectiveOfferSummaryEditionProps) => {
  const notify = useNotification()
  const navigate = useNavigate()
  const isMarseilleActive = useActiveFeature('WIP_ENABLE_MARSEILLE')

  const offerEditLink = `/offre/${computeURLCollectiveOfferId(
    offer.id,
    offer.isTemplate
  )}/collectif/edition`

  const stockEditLink = `/offre/${computeURLCollectiveOfferId(
    offer.id,
    offer.isTemplate
  )}/collectif/stocks/edition`

  const previewLink = `/offre/${computeURLCollectiveOfferId(
    offer.id,
    offer.isTemplate
  )}/collectif/preview`

  const visibilityEditLink = `/offre/${offer.id}/collectif/visibilite/edition`
  const { logEvent } = useAnalytics()

  return (
    <>
      <OfferEducationalActions
        className={styles.actions}
        isBooked={
          isCollectiveOfferTemplate(offer)
            ? false
            : Boolean(offer.collectiveStock?.isBooked)
        }
        offer={offer}
        reloadCollectiveOffer={reloadCollectiveOffer}
        mode={mode}
      />

      {offer.isTemplate && (
        <div className={styles['duplicate-offer']}>
          <ButtonLink
            link={{
              to: offerEditLink,
              isExternal: false,
            }}
            icon={fullEditIcon}
          >
            Modifier l’offre
          </ButtonLink>
          <ButtonLink
            link={{
              to: previewLink,
              isExternal: false,
            }}
            icon={fullShowIcon}
          >
            Aperçu dans ADAGE
          </ButtonLink>
          <Button
            variant={ButtonVariant.TERNARY}
            icon={fullMoreIcon}
            onClick={() => {
              logEvent?.(Events.CLICKED_DUPLICATE_TEMPLATE_OFFER, {
                from: OFFER_FROM_TEMPLATE_ENTRIES.OFFER_TEMPLATE_RECAP,
              })
              // eslint-disable-next-line @typescript-eslint/no-floating-promises
              createOfferFromTemplate(
                navigate,
                notify,
                offer.id,
                undefined,
                isMarseilleActive
              )
            }}
          >
            Créer une offre réservable
          </Button>
        </div>
      )}

      <CollectiveOfferSummary
        offer={offer}
        offerEditLink={offerEditLink}
        stockEditLink={stockEditLink}
        visibilityEditLink={visibilityEditLink}
      />

      <ActionsBarSticky>
        <ActionsBarSticky.Left>
          <ButtonLink
            variant={ButtonVariant.PRIMARY}
            link={{ isExternal: false, to: computeCollectiveOffersUrl({}) }}
          >
            Retour à la liste des offres
          </ButtonLink>
        </ActionsBarSticky.Left>
      </ActionsBarSticky>
    </>
  )
}

export default CollectiveOfferSummaryEdition
