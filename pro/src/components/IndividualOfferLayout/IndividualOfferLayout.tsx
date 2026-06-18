import type { ReactNode } from 'react'
import { useNavigate } from 'react-router'

import { api } from '@/apiClient/api'
import {
  type GetIndividualOfferWithAddressResponseModel,
  OfferStatus,
} from '@/apiClient/v1'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { getOfferEnhancementCardsVisibility } from '@/commons/core/Offers/utils/getOfferEnhancementCardsVisibility'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { SynchronizedProviderInformation } from '@/components/SynchronisedProviderInformation/SynchronizedProviderInformation'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullTrashIcon from '@/icons/full-trash.svg'

import { IndividualOfferNavigation } from './components/IndividualOfferNavigation/IndividualOfferNavigation'
import { OfferHeadlineCard } from './components/OfferHeadlineCard/OfferHeadlineCard'
import { OfferHighlightCard } from './components/OfferHighlightCard/OfferHighlightCard'
import { OfferPublicationEdition } from './components/OfferPublicationEdition/OfferPublicationEdition'
import { OfferRecommendationCard } from './components/OfferRecommendationCard/OfferRecommendationCard'
import { OfferStatusBanner } from './components/OfferStatusBanner/OfferStatusBanner'
import { Status } from './components/Status/Status'
import styles from './IndividualOfferLayout.module.scss'

export interface IndividualOfferLayoutProps {
  children: ReactNode
  offer: GetIndividualOfferWithAddressResponseModel | null
}

// TODO (igabriele, 2025-08-18): Get `offer` directly from context (DRY, complexity).
export const IndividualOfferLayout = ({
  children,
  offer,
}: IndividualOfferLayoutProps) => {
  const { hasPublishedOfferWithSameEan } = useIndividualOfferContext()
  const mode = useOfferWizardMode()
  const isOfferExposureEnabled = useActiveFeature('WIP_OFFER_EXPOSURE')

  // All offer's publication dates can be manually edited except for:
  // - rejected offers
  // - offers synchronized with a provider
  const canEditPublicationDates =
    !!offer && offer.status !== OfferStatus.REJECTED && !offer.lastProvider

  const displayUpdatePublicationAndBookingDates =
    offer &&
    canEditPublicationDates &&
    [
      OfferStatus.ACTIVE,
      OfferStatus.INACTIVE,
      OfferStatus.PUBLISHED,
      OfferStatus.SCHEDULED,
    ].includes(offer.status)

  const {
    shouldDisplayRecommendationCard,
    shouldDisplayHighlightCard,
    shouldDisplayHeadlineCard,
  } = getOfferEnhancementCardsVisibility(offer)

  const snackBar = useSnackBar()
  const navigate = useNavigate()

  const onDeleteOfferWithAlreadyExistingEan = async () => {
    if (!offer) {
      return
    }
    try {
      await api.deleteDraftOffers({ body: { ids: [offer.id] } })
    } catch {
      snackBar.error(
        'Une erreur s’est produite lors de la suppression de l’offre'
      )
      return
    }
    snackBar.success('Votre brouillon a bien été supprimé')
    navigate('/offres')
  }

  return (
    <>
      <div className={styles['title-container']}>
        {offer &&
          mode !== OFFER_WIZARD_MODE.CREATION &&
          (displayUpdatePublicationAndBookingDates ? (
            <OfferPublicationEdition offer={offer} />
          ) : (
            <span className={styles.status}>
              {
                <Status
                  offer={offer}
                  canEditPublicationDates={canEditPublicationDates}
                />
              }
            </span>
          ))}
      </div>
      {offer && mode !== OFFER_WIZARD_MODE.READ_ONLY && (
        <p className={styles['offer-title']}>{offer.name}</p>
      )}
      {offer && <OfferStatusBanner status={offer.status} />}
      {hasPublishedOfferWithSameEan && (
        <div className={styles['ean-already-exists-callout']}>
          <Banner
            variant={BannerVariants.ERROR}
            title="Votre brouillon d’offre est obsolète car vous avez déjà publié une offre avec cet EAN"
            description={
              <>
                <p className={styles['ean-already-exists-callout-description']}>
                  Vous ne pouvez pas publier 2 offres avec un EAN similaire.
                </p>
                <Button
                  onClick={onDeleteOfferWithAlreadyExistingEan}
                  variant={ButtonVariant.TERTIARY}
                  color={ButtonColor.NEUTRAL}
                  icon={fullTrashIcon}
                  label="Supprimer ce brouillon"
                />
              </>
            }
          />
        </div>
      )}
      {offer &&
        mode !== OFFER_WIZARD_MODE.CREATION &&
        !isOfferExposureEnabled && (
          <div className={styles['banner-container']}>
            {(shouldDisplayRecommendationCard ||
              shouldDisplayHighlightCard ||
              shouldDisplayHeadlineCard) && (
              <h2 className={styles['banner-container-title']}>
                Mises en avant de votre offre
              </h2>
            )}
            <div className={styles['cards-container']}>
              {shouldDisplayRecommendationCard && (
                <OfferRecommendationCard offerId={offer.id} />
              )}
              {shouldDisplayHighlightCard && (
                <OfferHighlightCard
                  offerId={offer.id}
                  highlightRequests={offer.highlightRequests}
                />
              )}
              {shouldDisplayHeadlineCard && (
                <OfferHeadlineCard
                  offerId={offer.id}
                  hasThumb={!!offer.thumbUrl}
                />
              )}
            </div>
          </div>
        )}

      {offer?.lastProvider?.name && (
        <div className={styles['banner-container']}>
          <SynchronizedProviderInformation
            providerName={offer.lastProvider.name}
          />
        </div>
      )}

      <IndividualOfferNavigation />

      <div className={styles.content}>{children}</div>
    </>
  )
}
