import React from 'react'

import useActiveFeature from 'components/hooks/useActiveFeature'
import useNotification from 'components/hooks/useNotification'
import {
  cancelCollectiveBookingAdapter,
  CollectiveOffer,
  CollectiveOfferTemplate,
  EducationalCategories,
  patchIsCollectiveOfferActiveAdapter,
  patchIsTemplateOfferActiveAdapter,
} from 'core/OfferEducational'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import OfferEducationalActions from 'new_components/OfferEducationalActions'
import { SummaryLayout } from 'new_components/SummaryLayout'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './CollectiveOfferSummary.module.scss'
import CollectiveOfferAccessibilitySection from './components/CollectiveOfferAccessibilitySection'
import CollectiveOfferContactSection from './components/CollectiveOfferContactSection'
import CollectiveOfferNotificationSection from './components/CollectiveOfferNotificationSection'
import CollectiveOfferParticipantSection from './components/CollectiveOfferParticipantSection'
import CollectiveOfferPracticalInformation from './components/CollectiveOfferPracticalInformation'
import CollectiveOfferStockSection from './components/CollectiveOfferStockSection'
import CollectiveOfferTypeSection from './components/CollectiveOfferTypeSection'
import CollectiveOfferVenueSection from './components/CollectiveOfferVenueSection'
import CollectiveOfferVisibilitySection from './components/CollectiveOfferVisibilitySection'
import { DEFAULT_RECAP_VALUE } from './components/constants'

interface ICollectiveOfferSummaryProps {
  offer: CollectiveOfferTemplate | CollectiveOffer
  categories: EducationalCategories
  reloadCollectiveOffer?: () => void
}

const CollectiveOfferSummary = ({
  offer,
  categories,
  reloadCollectiveOffer,
}: ICollectiveOfferSummaryProps) => {
  const notify = useNotification()

  /* istanbul ignore next: DEBT, TO FIX */
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

  /* istanbul ignore next: DEBT, TO FIX */
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

  const isCollectiveOfferDuplicationActive = useActiveFeature(
    'WIP_CREATE_COLLECTIVE_OFFER_FROM_TEMPLATE'
  )

  const offerEditLink = `/offre/${computeURLCollectiveOfferId(
    offer.id,
    offer.isTemplate
  )}/collectif/edition`

  const stockEditLink = `/offre/${computeURLCollectiveOfferId(
    offer.id,
    offer.isTemplate
  )}/collectif/stocks/edition`

  const visibilityEditLink = `/offre/${offer.id}/collectif/visibilite/edition`

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
      {isCollectiveOfferDuplicationActive && offer.isTemplate && (
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
            link={{
              isExternal: false,
              to: `/offre/duplication/collectif/${offer.id}`,
            }}
          >
            Créer une offre réservable pour un établissement scolaire
          </ButtonLink>
        </div>
      )}
      <SummaryLayout>
        <SummaryLayout.Content fullWidth>
          <SummaryLayout.Section
            title="Détails de l’offre"
            editLink={offerEditLink}
          >
            <CollectiveOfferVenueSection venue={offer.venue} />
            <CollectiveOfferTypeSection offer={offer} categories={categories} />
            <CollectiveOfferPracticalInformation offer={offer} />
            <CollectiveOfferParticipantSection students={offer.students} />
            <CollectiveOfferAccessibilitySection offer={offer} />
            <CollectiveOfferContactSection
              phone={offer.contactPhone}
              email={offer.contactEmail}
            />
            {offer.bookingEmails.length > 0 && (
              <CollectiveOfferNotificationSection
                bookingEmails={offer.bookingEmails}
              />
            )}
          </SummaryLayout.Section>
          <SummaryLayout.Section title="Date & Prix" editLink={stockEditLink}>
            {offer.isTemplate ? (
              <SummaryLayout.Row
                title="Détails"
                description={
                  offer.educationalPriceDetail || DEFAULT_RECAP_VALUE
                }
              />
            ) : (
              <CollectiveOfferStockSection
                stock={offer.collectiveStock}
                venueDepartmentCode={offer.venue.departementCode}
              />
            )}
          </SummaryLayout.Section>
          {!offer.isTemplate && (
            <SummaryLayout.Section
              title="Visibilité"
              editLink={visibilityEditLink}
            >
              <CollectiveOfferVisibilitySection
                institution={offer.institution}
              />
            </SummaryLayout.Section>
          )}
        </SummaryLayout.Content>
      </SummaryLayout>
      <ButtonLink
        variant={ButtonVariant.PRIMARY}
        link={{ isExternal: false, to: '/offers/collective' }}
      >
        Retour à la liste des offres
      </ButtonLink>
    </>
  )
}

export default CollectiveOfferSummary
