import cn from 'classnames'
import { addDays, isBefore } from 'date-fns'
import React from 'react'

import { DMSApplicationstatus } from 'apiClient/v1'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import {
  Events,
  OFFER_FORM_HOMEPAGE,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
  VenueEvents,
} from '../../../core/FirebaseEvents/constants'
import useActiveFeature from '../../../hooks/useActiveFeature'
import useAnalytics from '../../../hooks/useAnalytics'
import { CircleArrowIcon, HelpSIcon } from '../../../icons'
import { UNAVAILABLE_ERROR_PAGE } from '../../../utils/routes'

import styles from './VenueOfferSteps.module.scss'

interface IVenueOfferStepsProps {
  hasVenue: boolean
  hasMissingReimbursementPoint?: boolean
  offererId: string
  venueId?: string | null
  hasCreatedOffer?: boolean
  dmsStatus?: DMSApplicationstatus
  dmsInProgress?: boolean
  hasAdageId?: boolean
  adageInscriptionDate?: string | null
}

const VenueOfferSteps = ({
  offererId,
  hasVenue = false,
  hasMissingReimbursementPoint = true,
  venueId = null,
  hasCreatedOffer = false,
  dmsStatus,
  dmsInProgress = false,
  hasAdageId = false,
  adageInscriptionDate,
}: IVenueOfferStepsProps) => {
  const isVenueCreationAvailable = useActiveFeature('API_SIRENE_AVAILABLE')
  const venueCreationUrl = isVenueCreationAvailable
    ? `/structures/${offererId}/lieux/creation`
    : UNAVAILABLE_ERROR_PAGE
  const { logEvent } = useAnalytics()
  const isCollectiveDmsTrackingActive = useActiveFeature(
    'WIP_ENABLE_COLLECTIVE_DMS_TRACKING'
  )
  const hasAdageIdForMoreThan30Days =
    hasAdageId &&
    !!adageInscriptionDate &&
    isBefore(new Date(adageInscriptionDate), addDays(new Date(), -30))

  const shouldDisplayEACInformationSection =
    isCollectiveDmsTrackingActive &&
    !(dmsStatus === DMSApplicationstatus.REFUSE) &&
    dmsInProgress &&
    !hasAdageIdForMoreThan30Days

  return (
    <div
      className={cn(styles['card-wrapper'], 'h-card', {
        [styles['no-shadow']]: hasVenue,
      })}
      data-testid={hasVenue ? 'venue-offer-steps' : 'home-offer-steps'}
    >
      {!hasCreatedOffer && (
        <div className="h-card-inner">
          <h4>Prochaines étapes : </h4>

          <div className={styles['venue-offer-steps']}>
            {!hasVenue && (
              <div className={styles['step-venue-creation']}>
                <ButtonLink
                  className={styles['step-button-width']}
                  variant={ButtonVariant.BOX}
                  Icon={CircleArrowIcon}
                  link={{
                    to: venueCreationUrl,
                    isExternal: false,
                  }}
                  onClick={() => {
                    logEvent?.(Events.CLICKED_CREATE_VENUE, {
                      from: location.pathname,
                      is_first_venue: true,
                    })
                  }}
                >
                  Créer un lieu
                </ButtonLink>
                <ButtonLink
                  className={styles['step-button-width']}
                  variant={ButtonVariant.TERNARY}
                  link={{
                    to: 'https://aide.passculture.app/hc/fr/articles/4411992075281--Acteurs-Culturels-Comment-cr%C3%A9er-un-lieu-',
                    isExternal: true,
                    rel: 'noopener noreferrer',
                    target: '_blank',
                  }}
                  Icon={HelpSIcon}
                  onClick={() => {
                    logEvent?.(Events.CLICKED_NO_VENUE, {
                      from: location.pathname,
                    })
                  }}
                >
                  Je ne dispose pas de lieu propre, quel type de lieu créer ?
                </ButtonLink>
              </div>
            )}
            <ButtonLink
              className={styles['step-button-width']}
              isDisabled={!hasVenue}
              variant={ButtonVariant.BOX}
              Icon={CircleArrowIcon}
              link={{
                to: `/offre/creation?lieu=${venueId}&structure=${offererId}`,
                isExternal: false,
              }}
              onClick={() =>
                logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
                  from: OFFER_FORM_NAVIGATION_IN.HOME,
                  to: OFFER_FORM_HOMEPAGE,
                  used: OFFER_FORM_NAVIGATION_MEDIUM.VENUE_OFFER_STEPS,
                  isEdition: false,
                })
              }
            >
              Créer une offre
            </ButtonLink>
            {hasMissingReimbursementPoint && (
              <ButtonLink
                className={styles['step-button-width']}
                isDisabled={!hasVenue}
                variant={ButtonVariant.BOX}
                Icon={CircleArrowIcon}
                link={{
                  to: `/structures/${offererId}/lieux/${venueId}#reimbursement`,
                  isExternal: false,
                }}
                onClick={() => {
                  logEvent?.(VenueEvents.CLICKED_VENUE_ADD_RIB_BUTTON, {
                    venue_id: venueId || '',
                    from: OFFER_FORM_NAVIGATION_IN.HOME,
                  })
                }}
              >
                Renseigner des coordonnées bancaires
              </ButtonLink>
            )}
            {dmsStatus !== DMSApplicationstatus.REFUSE &&
              !hasAdageIdForMoreThan30Days && (
                <ButtonLink
                  className={styles['step-button-width']}
                  isDisabled={!hasAdageId}
                  variant={ButtonVariant.BOX}
                  Icon={CircleArrowIcon}
                  link={{
                    to: `/structures/${offererId}/lieux/${venueId}/eac`,
                    isExternal: false,
                  }}
                >
                  Renseigner mes informations à destination des enseignants
                </ButtonLink>
              )}
          </div>
        </div>
      )}
      {shouldDisplayEACInformationSection && (
        <div className="h-card-inner">
          <h4>Démarche en cours : </h4>

          <div className={styles['venue-offer-steps']}>
            <div className={styles['step-venue-creation']}>
              <ButtonLink
                className={styles['step-button-width']}
                variant={ButtonVariant.BOX}
                Icon={CircleArrowIcon}
                link={{
                  to: `/structures/${offererId}/lieux/${venueId}#reimbursement`,
                  isExternal: false,
                }}
              >
                Suivre ma demande de référencement ADAGE
              </ButtonLink>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default VenueOfferSteps
