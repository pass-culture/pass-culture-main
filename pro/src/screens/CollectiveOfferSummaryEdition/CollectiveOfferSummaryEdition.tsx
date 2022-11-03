import React from 'react'

import {
  Events,
  OFFER_FROM_TEMPLATE_ENTRIES,
} from 'core/FirebaseEvents/constants'
import {
  cancelCollectiveBookingAdapter,
  CollectiveOffer,
  CollectiveOfferTemplate,
  EducationalCategories,
  patchIsCollectiveOfferActiveAdapter,
  patchIsTemplateOfferActiveAdapter,
} from 'core/OfferEducational'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import CollectiveOfferSummary from 'new_components/CollectiveOfferSummary'
import OfferEducationalActions from 'new_components/OfferEducationalActions'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './CollectiveOfferSummaryEdition.module.scss'

interface CollectiveOfferSummaryEditionProps {
  offer: CollectiveOfferTemplate | CollectiveOffer
  categories: EducationalCategories
  reloadCollectiveOffer?: () => void
}

const CollectiveOfferSummaryEdition = ({
  offer,
  categories,
  reloadCollectiveOffer,
}: CollectiveOfferSummaryEditionProps) => {
  const notify = useNotification()

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
    })

    if (!isOk) {
      return notify.error(message)
    }

    notify.success(message)
    reloadCollectiveOffer?.()
  }

  const { logEvent } = useAnalytics()

  const setIsOfferActive = async () => {
    const adapter = offer.isTemplate
      ? patchIsTemplateOfferActiveAdapter
      : patchIsCollectiveOfferActiveAdapter

    const response = await adapter({
      offerId: offer.id,
      isActive: !offer.isActive,
    })

    if (response.isOk) {
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
        isCancellable={offer.isCancellable}
        isOfferActive={offer.isActive}
        setIsOfferActive={setIsOfferActive}
      />
      {offer.isTemplate && (
        <div className={styles['duplicate-offer']}>
          <p className={styles['duplicate-offer-description']}>
            Vous pouvez dupliquer cette offre autant de fois que vous le
            souhaitez pour l’associer aux établissements scolaires qui vous
            contactent. <br />
            &nbsp;· L’offre vitrine restera visible sur ADAGE <br />
            &nbsp;· L’offre associée à l’établissement devra être pré-réservée
            par l’enseignant(e) qui vous a contacté
          </p>
          <ButtonLink
            variant={ButtonVariant.PRIMARY}
            onClick={() =>
              logEvent?.(Events.CLICKED_DUPLICATE_TEMPLATE_OFFER, {
                from: OFFER_FROM_TEMPLATE_ENTRIES.OFFER_TEMPLATE_RECAP,
              })
            }
            link={{
              isExternal: false,
              to: `/offre/duplication/collectif/${offer.id}`,
            }}
          >
            Créer une offre réservable pour un établissement scolaire
          </ButtonLink>
        </div>
      )}
      <CollectiveOfferSummary
        offer={offer}
        categories={categories}
        offerEditLink={offerEditLink}
        stockEditLink={stockEditLink}
        visibilityEditLink={visibilityEditLink}
      />
      <ButtonLink
        variant={ButtonVariant.PRIMARY}
        link={{ isExternal: false, to: '/offers/collective' }}
      >
        Retour à la liste des offres
      </ButtonLink>
    </>
  )
}

export default CollectiveOfferSummaryEdition
