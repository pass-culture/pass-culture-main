import cn from 'classnames'
import React from 'react'

import {
  GetOffererResponseModel,
  GetOffererVenueResponseModel,
} from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { useActiveFeature } from 'hooks/useActiveFeature'
import fullInfoIcon from 'icons/full-info.svg'
import fullNextIcon from 'icons/full-next.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import {
  Events,
  OFFER_FORM_NAVIGATION_IN,
  VenueEvents,
} from '../../../core/FirebaseEvents/constants'
import { UNAVAILABLE_ERROR_PAGE } from '../../../utils/routes'
import { Card } from '../Card'
import {
  shouldDisplayEACInformationSectionForVenue,
  shouldShowVenueOfferStepsForVenue,
} from '../venueUtils'

import styles from './VenueOfferSteps.module.scss'

export interface VenueOfferStepsProps {
  offerer: GetOffererResponseModel
  venue?: GetOffererVenueResponseModel
  hasVenue: boolean
  isFirstVenue?: boolean
  isInsidePartnerBlock?: boolean
  className?: string
}

export const VenueOfferSteps = ({
  offerer,
  venue,
  hasVenue = false,
  isFirstVenue = false,
  isInsidePartnerBlock = false,
  className,
}: VenueOfferStepsProps) => {
  const { logEvent } = useAnalytics()
  const isVenueCreationAvailable = useActiveFeature('API_SIRENE_AVAILABLE')

  const venueCreationUrl = isVenueCreationAvailable
    ? `/structures/${offerer.id}/lieux/creation`
    : UNAVAILABLE_ERROR_PAGE

  /* Condition linked to add bank account banner
    display button if this is the first venue and the offerer has no offer at all,
    or if the offerer has no paid offerer
  */
  const offererHasCreatedOffer = Boolean(
    offerer.managedVenues?.some((venue) => venue.hasCreatedOffer)
  )
  const offererHasBankAccount = Boolean(
    offerer.hasPendingBankAccount || offerer.hasValidBankAccount
  )
  const displayButtonDependingVenue =
    (!isFirstVenue && !offerer.hasNonFreeOffer) ||
    (isFirstVenue && !offererHasCreatedOffer)

  const shouldDisplayEACInformationSection =
    shouldDisplayEACInformationSectionForVenue(venue)
  const shouldShowVenueOfferSteps = shouldShowVenueOfferStepsForVenue(venue)

  if (!shouldShowVenueOfferSteps) {
    return null
  }

  return (
    <Card
      className={cn(styles['card-wrapper'], className, {
        [styles['no-shadow']]: hasVenue || isInsidePartnerBlock,
        [styles['inside-partner-block']]: isInsidePartnerBlock,
      })}
      data-testid={hasVenue ? 'venue-offer-steps' : 'home-offer-steps'}
    >
      {(!venue?.hasCreatedOffer || shouldDisplayEACInformationSection) && (
        <>
          <h3 className={styles['card-title']}>Prochaines étapes : </h3>

          <div className={styles['venue-offer-steps']}>
            {!hasVenue && (
              <div className={styles['step-venue-creation']}>
                <ButtonLink
                  className={cn(
                    styles['step-button-width-info'],
                    styles['step-button-with-info']
                  )}
                  variant={ButtonVariant.BOX}
                  icon={fullNextIcon}
                  link={{
                    to: venueCreationUrl,
                  }}
                  onClick={() => {
                    logEvent(Events.CLICKED_CREATE_VENUE, {
                      from: location.pathname,
                      is_first_venue: true,
                    })
                  }}
                >
                  Créer un lieu
                </ButtonLink>

                <ButtonLink
                  className={cn(
                    styles['step-button-width-info'],
                    styles['step-button-info']
                  )}
                  variant={ButtonVariant.QUATERNARY}
                  link={{
                    to: 'https://aide.passculture.app/hc/fr/articles/4411992075281--Acteurs-Culturels-Comment-cr%C3%A9er-un-lieu-',
                    isExternal: true,
                    target: '_blank',
                  }}
                  icon={fullInfoIcon}
                  onClick={() => {
                    logEvent(Events.CLICKED_NO_VENUE, {
                      from: location.pathname,
                    })
                  }}
                >
                  <span className={styles['step-button-info-text']}>
                    Je ne dispose pas de lieu propre, quel type de lieu créer ?
                  </span>
                </ButtonLink>
              </div>
            )}

            {venue && !venue.hasCreatedOffer && (
              <ButtonLink
                className={styles['step-button-width']}
                isDisabled={!hasVenue}
                variant={ButtonVariant.BOX}
                icon={fullNextIcon}
                link={{
                  to: `/offre/creation?lieu=${venue.id}&structure=${offerer.id}`,
                }}
              >
                Créer une offre
              </ButtonLink>
            )}

            {!offererHasBankAccount && displayButtonDependingVenue && (
              <ButtonLink
                className={styles['step-button-width']}
                isDisabled={!hasVenue}
                variant={ButtonVariant.BOX}
                icon={fullNextIcon}
                link={{
                  to: `remboursements/informations-bancaires?structure=${offerer.id}`,
                }}
                onClick={() => {
                  logEvent(VenueEvents.CLICKED_VENUE_ADD_RIB_BUTTON, {
                    venue_id: venue?.id ?? '',
                    from: OFFER_FORM_NAVIGATION_IN.HOME,
                  })
                }}
              >
                Ajouter un compte bancaire
              </ButtonLink>
            )}
            {venue && shouldDisplayEACInformationSection && (
              <ButtonLink
                className={styles['step-button-width']}
                isDisabled={!venue.hasAdageId}
                variant={ButtonVariant.BOX}
                icon={fullNextIcon}
                link={{
                  to: `/structures/${offerer.id}/lieux/${venue.id}/collectif`,
                }}
              >
                Renseigner mes informations à destination des enseignants
              </ButtonLink>
            )}
          </div>
        </>
      )}

      {venue && shouldDisplayEACInformationSection && (
        <>
          <h3 className={styles['card-title']}>Démarche en cours : </h3>

          <div className={styles['venue-offer-steps']}>
            <ButtonLink
              className={styles['step-button-width']}
              variant={ButtonVariant.BOX}
              icon={fullNextIcon}
              link={{
                to: `/structures/${offerer.id}/lieux/${venue.id}/collectif`,
              }}
              onClick={() => {
                logEvent(Events.CLICKED_EAC_DMS_TIMELINE, {
                  from: location.pathname,
                })
              }}
            >
              Suivre ma demande de référencement ADAGE
            </ButtonLink>
          </div>
        </>
      )}
    </Card>
  )
}
