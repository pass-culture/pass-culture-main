import cn from 'classnames'
import React from 'react'

import fullInfoIcon from 'icons/full-info.svg'
import fullLinkIcon from 'icons/full-link.svg'
import fullNextIcon from 'icons/full-next.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import {
  Events,
  OFFER_FORM_NAVIGATION_IN,
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
  offererHasBankAccount: boolean
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
  offererHasBankAccount,
  demarchesSimplifieesApplicationId,
}: VenueOfferStepsProps) => {
  const isVenueCreationAvailable = useActiveFeature('API_SIRENE_AVAILABLE')
  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )
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
                      className={cn(
                        styles['step-button-width-info'],
                        styles['step-button-info']
                      )}
                      variant={ButtonVariant.QUATERNARY}
                      link={{
                        to: 'https://aide.passculture.app/hc/fr/articles/4411992075281--Acteurs-Culturels-Comment-cr%C3%A9er-un-lieu-',
                        isExternal: true,
                        rel: 'noopener noreferrer',
                        target: '_blank',
                      }}
                      icon={fullInfoIcon}
                      onClick={() => {
                        logEvent?.(Events.CLICKED_NO_VENUE, {
                          from: location.pathname,
                        })
                      }}
                    >
                      <span className={styles['step-button-info-text']}>
                        Je ne dispose pas de lieu propre, quel type de lieu
                        créer ?
                      </span>
                    </ButtonLink>
                  </div>
                )}
                {!hasCreatedOffer && (
                  <ButtonLink
                    className={styles['step-button-width']}
                    isDisabled={!hasVenue}
                    variant={ButtonVariant.BOX}
                    icon={fullNextIcon}
                    link={{
                      to: `/offre/creation?lieu=${venueId}&structure=${offererId}`,
                      isExternal: false,
                    }}
                  >
                    Créer une offre
                  </ButtonLink>
                )}
                {!isNewBankDetailsJourneyEnabled &&
                  hasMissingReimbursementPoint && (
                    <ButtonLink
                      className={styles['step-button-width']}
                      isDisabled={!hasVenue}
                      variant={ButtonVariant.BOX}
                      icon={fullNextIcon}
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
                {isNewBankDetailsJourneyEnabled &&
                  !hasCreatedOffer &&
                  !offererHasBankAccount && (
                    <ButtonLink
                      className={styles['step-button-width']}
                      isDisabled={!hasVenue}
                      variant={ButtonVariant.BOX}
                      icon={fullNextIcon}
                      link={{
                        to: `remboursements/informations-bancaires?structure=${offererId}`,
                        isExternal: false,
                      }}
                      onClick={() => {
                        logEvent?.(VenueEvents.CLICKED_VENUE_ADD_RIB_BUTTON, {
                          venue_id: venueId ?? '',
                          from: OFFER_FORM_NAVIGATION_IN.HOME,
                        })
                      }}
                    >
                      Ajouter un compte bancaire
                    </ButtonLink>
                  )}
                {shouldDisplayEACInformationSection && (
                  <ButtonLink
                    className={styles['step-button-width']}
                    isDisabled={!hasAdageId}
                    variant={ButtonVariant.BOX}
                    icon={fullNextIcon}
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
            (!isNewBankDetailsJourneyEnabled &&
              hasPendingBankInformationApplication)) && (
            <div className="h-card-inner">
              <h3 className={styles['card-title']}>Démarche en cours : </h3>

              <div className={styles['venue-offer-steps']}>
                {shouldDisplayEACInformationSection && (
                  <ButtonLink
                    className={styles['step-button-width']}
                    variant={ButtonVariant.BOX}
                    icon={fullNextIcon}
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
                {!isNewBankDetailsJourneyEnabled &&
                  hasPendingBankInformationApplication && (
                    <ButtonLink
                      className={styles['step-button-width']}
                      variant={ButtonVariant.BOX}
                      icon={fullLinkIcon}
                      link={{
                        to: `https://www.demarches-simplifiees.fr/dossiers${
                          demarchesSimplifieesApplicationId
                            ? `/${demarchesSimplifieesApplicationId}/messagerie`
                            : ''
                        }`,
                        isExternal: true,
                        target: '_blank',
                      }}
                      onClick={() => {
                        logEvent?.(
                          VenueEvents.CLICKED_BANK_DETAILS_RECORD_FOLLOW_UP,
                          {
                            from: location.pathname,
                          }
                        )
                      }}
                    >
                      Suivre mon dossier de coordonnées bancaires
                    </ButtonLink>
                  )}
              </div>
            </div>
          )}
        </div>
      )}
    </>
  )
}

export default VenueOfferSteps
