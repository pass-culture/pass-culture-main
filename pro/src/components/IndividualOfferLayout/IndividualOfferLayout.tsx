import type { ReactNode } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router'

import { api } from '@/apiClient/api'
import {
  type GetIndividualOfferWithAddressResponseModel,
  OfferStatus,
} from '@/apiClient/v1'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { useHasAccessToDidacticOnboarding } from '@/commons/hooks/useHasAccessToDidacticOnboarding'
import { useNotification } from '@/commons/hooks/useNotification'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { SynchronizedProviderInformation } from '@/components/SynchronisedProviderInformation/SynchronizedProviderInformation'
import { Tag, TagVariant } from '@/design-system/Tag/Tag'
import fullTrashIcon from '@/icons/full-trash.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { Callout } from '@/ui-kit/Callout/Callout'
import { CalloutVariant } from '@/ui-kit/Callout/types'

import styles from './IndividualOfferLayout.module.scss'
import { IndividualOfferNavigation } from './IndividualOfferNavigation/IndividualOfferNavigation'
import { OfferPublicationEdition } from './OfferPublicationEdition/OfferPublicationEdition'
import { OfferStatusBanner } from './OfferStatusBanner/OfferStatusBanner'
import { Status } from './Status/Status'

export interface IndividualOfferLayoutProps {
  withStepper?: boolean
  children: ReactNode
  offer: GetIndividualOfferWithAddressResponseModel | null
}

// TODO (igabriele, 2025-08-18): Get `offer` directly from context (DRY, complexity).
export const IndividualOfferLayout = ({
  children,
  withStepper = true,
  offer,
}: IndividualOfferLayoutProps) => {
  const { hasPublishedOfferWithSameEan } = useIndividualOfferContext()
  const mode = useOfferWizardMode()
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const isDidacticOnboardingEnabled = useHasAccessToDidacticOnboarding()

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

  const shouldDisplayActionOnStatus =
    withStepper && !displayUpdatePublicationAndBookingDates

  const notify = useNotification()
  const navigate = useNavigate()

  if (isOnboarding && isDidacticOnboardingEnabled === false) {
    return <Navigate to="/accueil" />
  }

  const onDeleteOfferWithAlreadyExistingEan = async () => {
    if (!offer) {
      return
    }
    try {
      await api.deleteDraftOffers({ ids: [offer.id] })
    } catch {
      notify.error(
        'Une erreur s’est produite lors de la suppression de l’offre'
      )
      return
    }
    notify.success('Votre brouillon a bien été supprimé')
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate('/offres')
  }

  return (
    <>
      <div className={styles['title-container']}>
        {offer && mode !== OFFER_WIZARD_MODE.CREATION && (
          <>
            {shouldDisplayActionOnStatus && (
              <span className={styles.status}>
                {
                  <Status
                    offer={offer}
                    canEditPublicationDates={canEditPublicationDates}
                  />
                }
              </span>
            )}
            {displayUpdatePublicationAndBookingDates && (
              <OfferPublicationEdition offer={offer} />
            )}
          </>
        )}
      </div>

      {offer && (
        <p className={styles['offer-title']}>
          {offer.name}
          {offer.isHeadlineOffer && (
            <Tag label="Offre à la une" variant={TagVariant.HEADLINE} />
          )}
        </p>
      )}

      {offer && withStepper && <OfferStatusBanner status={offer.status} />}

      {hasPublishedOfferWithSameEan && (
        <Callout
          variant={CalloutVariant.ERROR}
          title="Votre brouillon d’offre est obsolète car vous avez déjà publié une offre avec cet EAN"
          className={styles['ean-already-exists-callout']}
        >
          <p className={styles['ean-already-exists-callout-description']}>
            Vous ne pouvez pas publier 2 offres avec un EAN similaire.
          </p>
          <Button
            onClick={onDeleteOfferWithAlreadyExistingEan}
            variant={ButtonVariant.TERNARY}
            icon={fullTrashIcon}
            className={styles['ean-already-exists-callout-button']}
          >
            Supprimer ce brouillon
          </Button>
        </Callout>
      )}

      {offer?.lastProvider?.name && (
        <div className={styles['banner-container']}>
          <SynchronizedProviderInformation
            providerName={offer.lastProvider.name}
          />
        </div>
      )}

      {withStepper && <IndividualOfferNavigation />}

      <div className={styles.content}>{children}</div>
    </>
  )
}
