import cn from 'classnames'
import { useState } from 'react'

import type {
  GetOffererResponseModel,
  GetOffererVenueResponseModel,
  VenueListItemResponseModel,
} from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { VenueEvents } from '@/commons/core/FirebaseEvents/constants'
import { Card } from '@/components/Card/Card'
import { Tag, TagVariant } from '@/design-system/Tag/Tag'
import fullDisclosureCloseIcon from '@/icons/full-disclosure-close.svg'
import fullDisclosureOpenIcon from '@/icons/full-disclosure-open.svg'
import { shouldShowVenueOfferStepsForVenue } from '@/pages/Homepage/components/Offerers/components/VenueList/venueUtils'
import { VenueOfferSteps } from '@/pages/Homepage/components/VenueOfferSteps/VenueOfferSteps'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './Venue.module.scss'

export interface VenueProps {
  offerer: GetOffererResponseModel | null
  venue: GetOffererVenueResponseModel | VenueListItemResponseModel
  isFirstVenue?: boolean
}

export const Venue = ({ offerer, venue, isFirstVenue = false }: VenueProps) => {
  const shouldShowVenueOfferSteps = shouldShowVenueOfferStepsForVenue(venue)
  console.log({ venue })
  console.log({ shouldShowVenueOfferSteps })

  const [prevInitialOpenState, setPrevInitialOpenState] = useState(
    shouldShowVenueOfferSteps
  )
  const [prevOffererId, setPrevOffererId] = useState(offerer?.id)
  const [isToggleOpen, setIsToggleOpen] = useState(shouldShowVenueOfferSteps)
  const { logEvent } = useAnalytics()

  const venueIdTrackParam = {
    venue_id: venue.id,
  }

  if (prevInitialOpenState !== shouldShowVenueOfferSteps) {
    setIsToggleOpen(shouldShowVenueOfferSteps)
    setPrevInitialOpenState(shouldShowVenueOfferSteps)
  }

  if (offerer?.id !== prevOffererId) {
    setPrevOffererId(offerer?.id)
  }

  const editVenueLink = `/structures/${offerer?.id}/lieux/${venue.id}`
  const venueDisplayName = venue.isVirtual
    ? 'Offres numériques'
    : venue.publicName || venue.name

  return (
    <Card data-testid="venue-wrapper">
      <div className={styles['header-row']}>
        <h3 className={styles['toggle-wrapper']}>
          {shouldShowVenueOfferSteps ? (
            <button
              className={cn(styles['venue-name'], styles['venue-name-button'])}
              type="button"
              onClick={() => {
                setIsToggleOpen((prev) => !prev)
                logEvent(
                  VenueEvents.CLICKED_VENUE_ACCORDION_BUTTON,
                  venueIdTrackParam
                )
              }}
            >
              <SvgIcon
                alt={`${
                  isToggleOpen ? 'Masquer' : 'Afficher'
                } les statistiques`}
                className={styles['toggle-icon']}
                src={
                  isToggleOpen
                    ? fullDisclosureOpenIcon
                    : fullDisclosureCloseIcon
                }
              />
              <span data-testid={`venue-name-span-${venue.id}`}>
                {venueDisplayName}
              </span>
            </button>
          ) : (
            <div
              className={styles['venue-name']}
              data-testid={`venue-name-div-${venue.id}`}
            >
              {venueDisplayName}
            </div>
          )}

          {venue.hasVenueProviders && (
            <div className={styles['api-tag']}>
              <Tag label="API" variant={TagVariant.DEFAULT} />
            </div>
          )}
        </h3>

        <div className={styles['button-group']}>
          <ButtonLink
            variant={ButtonVariant.SECONDARY}
            to={editVenueLink}
            aria-label={`Gérer la page de ${venueDisplayName}`}
            onClick={() =>
              logEvent(
                VenueEvents.CLICKED_VENUE_PUBLISHED_OFFERS_LINK,
                venueIdTrackParam
              )
            }
          >
            Gérer ma page
          </ButtonLink>
        </div>
      </div>

      {isToggleOpen && shouldShowVenueOfferSteps && offerer && (
        <div className={styles['offer-steps']}>
          <VenueOfferSteps
            offerer={offerer}
            venue={venue}
            hasVenue
            isFirstVenue={isFirstVenue}
          />
        </div>
      )}
    </Card>
  )
}
