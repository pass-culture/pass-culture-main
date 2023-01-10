import React, { useState } from 'react'
import { useHistory } from 'react-router'

import ActionsBarSticky from 'components/ActionsBarSticky'
import CollectiveOfferSummary from 'components/CollectiveOfferSummary'
import OfferEducationalActions from 'components/OfferEducationalActions'
import {
  Events,
  OFFER_FROM_TEMPLATE_ENTRIES,
} from 'core/FirebaseEvents/constants'
import {
  cancelCollectiveBookingAdapter,
  CollectiveOffer,
  CollectiveOfferTemplate,
  createOfferFromTemplate,
  EducationalCategories,
  patchIsCollectiveOfferActiveAdapter,
  patchIsTemplateOfferActiveAdapter,
} from 'core/OfferEducational'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import { computeCollectiveOffersUrl } from 'core/Offers'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './CollectiveOfferSummaryEdition.module.scss'

interface CollectiveOfferSummaryEditionProps {
  offer: CollectiveOfferTemplate | CollectiveOffer
  categories: EducationalCategories
  reloadCollectiveOffer: () => void
}

const CollectiveOfferSummaryEdition = ({
  offer,
  categories,
  reloadCollectiveOffer,
}: CollectiveOfferSummaryEditionProps) => {
  const [isActive, setIsActive] = useState(offer.isActive)
  const notify = useNotification()
  const history = useHistory()

  const offerEditLink = `/offre/${computeURLCollectiveOfferId(
    offer.id,
    offer.isTemplate
  )}/collectif/edition`

  const stockEditLink = `/offre/${computeURLCollectiveOfferId(
    offer.id,
    offer.isTemplate
  )}/collectif/stocks/edition`

  const visibilityEditLink = `/offre/${offer.id}/collectif/visibilite/edition`

  const cancelActiveBookings = async () => {
    if (offer.isTemplate) {
      return
    }

    const { isOk, message } = await cancelCollectiveBookingAdapter({
      offerId: offer.id,
      offerStatus: offer.status,
    })

    if (!isOk) {
      return notify.error(message)
    }

    notify.success(message)
    reloadCollectiveOffer()
  }

  const { logEvent } = useAnalytics()

  const setIsOfferActive = async () => {
    const adapter = offer.isTemplate
      ? patchIsTemplateOfferActiveAdapter
      : patchIsCollectiveOfferActiveAdapter

    const response = await adapter({
      offerId: offer.id,
      isActive: !isActive,
    })

    if (response.isOk) {
      setIsActive(!isActive)
      reloadCollectiveOffer()
      return notify.success(response.message)
    }
    notify.error(response.message)
  }

  return (
    <>
      <OfferEducationalActions
        cancelActiveBookings={cancelActiveBookings}
        className={styles.actions}
        isBooked={
          offer.isTemplate ? false : Boolean(offer.collectiveStock?.isBooked)
        }
        offer={offer}
        isOfferActive={isActive}
        setIsOfferActive={setIsOfferActive}
      />
      {offer.isTemplate && (
        <div className={styles['duplicate-offer']}>
          <p className={styles['duplicate-offer-description']}>
            Vous pouvez dupliquer cette offre autant de fois que vous le
            souhaitez pour l’associer aux établissements scolaires qui vous
            contactent. <br />
            &nbsp;· L’offre vitrine restera visible sur ADAGE <br />
            &nbsp;· L’offre associée à l’établissement devra être préréservée
            par l’enseignant(e) qui vous a contacté
          </p>
          <Button
            variant={ButtonVariant.PRIMARY}
            onClick={() => {
              logEvent?.(Events.CLICKED_DUPLICATE_TEMPLATE_OFFER, {
                from: OFFER_FROM_TEMPLATE_ENTRIES.OFFER_TEMPLATE_RECAP,
              })
              createOfferFromTemplate(history, notify, offer.id)
            }}
          >
            Créer une offre réservable pour un établissement scolaire
          </Button>
        </div>
      )}
      <CollectiveOfferSummary
        offer={offer}
        categories={categories}
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
