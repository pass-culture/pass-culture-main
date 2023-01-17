import cn from 'classnames'
import React from 'react'

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
  hasOffer?: boolean
  hasMissingReimbursementPoint?: boolean
  offererId: string
  venueId?: string | null
}
const VenueOfferSteps = ({
  offererId,
  hasVenue = false,
  hasOffer = false,
  hasMissingReimbursementPoint = true,
  venueId = null,
}: IVenueOfferStepsProps) => {
  const isVenueCreationAvailable = useActiveFeature('API_SIRENE_AVAILABLE')
  const venueCreationUrl = isVenueCreationAvailable
    ? `/structures/${offererId}/lieux/creation`
    : UNAVAILABLE_ERROR_PAGE
  const { logEvent } = useAnalytics()

  return (
    <div
      className={cn(styles['card-wrapper'], 'h-card', {
        [styles['no-shadow']]: hasVenue,
      })}
      data-testid={hasVenue ? 'venue-offer-steps' : 'home-offer-steps'}
    >
      <div className="h-card-inner">
        <h4>Prochaines étapes : </h4>

        <div className={styles['venue-offer-steps']}>
          {!hasVenue && (
            <div className={styles['step-venue-creation']}>
              <ButtonLink
                variant={ButtonVariant.BOX}
                Icon={CircleArrowIcon}
                link={{
                  to: venueCreationUrl,
                  isExternal: false,
                }}
                onClick={() => {
                  logEvent?.(Events.CLICKED_CREATE_VENUE, {
                    from: location.pathname,
                  })
                  logEvent?.(Events.CLICKED_ADD_FIRST_VENUE_IN_OFFERER, {
                    from: location.pathname,
                  })
                }}
              >
                Créer un lieu
              </ButtonLink>
              <ButtonLink
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
          {!hasOffer && (
            <ButtonLink
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
          )}
          {hasMissingReimbursementPoint && (
            <ButtonLink
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
                })
              }}
            >
              Renseigner des coordonnées bancaires
            </ButtonLink>
          )}
        </div>
      </div>
    </div>
  )
}

export default VenueOfferSteps
