import cn from 'classnames'
import React from 'react'

import { ReactComponent as FullInfoIcon } from 'icons/full-info.svg'
import { ReactComponent as FullLinkIcon } from 'icons/full-link.svg'
import { ReactComponent as FullNextIcon } from 'icons/full-next.svg'
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
import { UNAVAILABLE_ERROR_PAGE } from '../../../utils/routes'

import styles from './VenueOfferSteps.module.scss'

export interface VenueOfferStepsProps {
  hasVenue: boolean
  hasMissingReimbursementPoint?: boolean
  offererId: number
  venueId?: number | null
  hasCreatedOffer?: boolean
  hasAdageId?: boolean
  shouldDisplayEACInformationSection?: boolean
  hasPendingBankInformationApplication?: boolean | null
  demarchesSimplifieesApplicationId?: number | null
}

const VenueOfferSteps = ({
  offererId,
  hasVenue = false,
  hasMissingReimbursementPoint = true,
  venueId = null,
  hasCreatedOffer = false,
  hasAdageId = false,
  shouldDisplayEACInformationSection = false,
  hasPendingBankInformationApplication = false,
  demarchesSimplifieesApplicationId,
}: VenueOfferStepsProps) => {
  const isVenueCreationAvailable = useActiveFeature('API_SIRENE_AVAILABLE')
  const venueCreationUrl = isVenueCreationAvailable
    ? `/structures/${offererId}/lieux/creation`
    : UNAVAILABLE_ERROR_PAGE
  const { logEvent } = useAnalytics()

  return (
    <>
      {(!hasCreatedOffer ||
        shouldDisplayEACInformationSection ||
        hasPendingBankInformationApplication) && (
        <div
          className={cn(styles['card-wrapper'], 'h-card', {
            [styles['no-shadow']]: hasVenue,
          })}
          data-testid={hasVenue ? 'venue-offer-steps' : 'home-offer-steps'}
        >
          {(!hasCreatedOffer || shouldDisplayEACInformationSection) && (
            <div className="h-card-inner">
              <h4>Prochaines étapes : </h4>

              <div className={styles['venue-offer-steps']}>
                {!hasVenue && (
                  <div className={styles['step-venue-creation']}>
                    <ButtonLink
                      className={styles['step-button-width']}
                      variant={ButtonVariant.BOX}
                      Icon={FullNextIcon}
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
                      Icon={FullInfoIcon}
                      onClick={() => {
                        logEvent?.(Events.CLICKED_NO_VENUE, {
                          from: location.pathname,
                        })
                      }}
                    >
                      Je ne dispose pas de lieu propre, quel type de lieu créer
                      ?
                    </ButtonLink>
                  </div>
                )}
                {!hasCreatedOffer && (
                  <ButtonLink
                    className={styles['step-button-width']}
                    isDisabled={!hasVenue}
                    variant={ButtonVariant.BOX}
                    Icon={FullNextIcon}
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
                )}
                {hasMissingReimbursementPoint && (
                  <ButtonLink
                    className={styles['step-button-width']}
                    isDisabled={!hasVenue}
                    variant={ButtonVariant.BOX}
                    Icon={FullNextIcon}
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
                {shouldDisplayEACInformationSection && (
                  <ButtonLink
                    className={styles['step-button-width']}
                    isDisabled={!hasAdageId}
                    variant={ButtonVariant.BOX}
                    Icon={FullNextIcon}
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
          {(shouldDisplayEACInformationSection ||
            hasPendingBankInformationApplication) && (
            <div className="h-card-inner">
              <h4>Démarche en cours : </h4>

              <div className={styles['venue-offer-steps']}>
                <div className={styles['step-venue-creation']}>
                  {shouldDisplayEACInformationSection && (
                    <ButtonLink
                      className={styles['step-button-width']}
                      variant={ButtonVariant.BOX}
                      Icon={FullNextIcon}
                      link={{
                        to: `/structures/${offererId}/lieux/${venueId}#venue-collective-data`,
                        isExternal: false,
                      }}
                      onClick={() => {
                        logEvent?.(Events.CLICKED_EAC_DMS_TIMELINE, {
                          from: location.pathname,
                        })
                      }}
                    >
                      Suivre ma demande de référencement ADAGE
                    </ButtonLink>
                  )}
                  {hasPendingBankInformationApplication && (
                    <ButtonLink
                      className={styles['step-button-width']}
                      variant={ButtonVariant.BOX}
                      Icon={FullLinkIcon}
                      link={{
                        to: `https://www.demarches-simplifiees.fr/dossiers${
                          demarchesSimplifieesApplicationId
                            ? `/${demarchesSimplifieesApplicationId}/messagerie`
                            : ''
                        }`,
                        isExternal: true,
                        target: '_blank',
                      }}
                    >
                      Suivre mon dossier de coordonnées bancaires
                    </ButtonLink>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </>
  )
}

export default VenueOfferSteps
