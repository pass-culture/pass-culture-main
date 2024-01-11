import cn from 'classnames'
import React, { useState } from 'react'

import {
  GetOffererResponseModel,
  GetOffererVenueResponseModel,
} from 'apiClient/v1'
import { VenueEvents } from 'core/FirebaseEvents/constants'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import fullDisclosureClose from 'icons/full-disclosure-close.svg'
import fullDisclosureOpen from 'icons/full-disclosure-open.svg'
import fullErrorIcon from 'icons/full-error.svg'
import fullMoreIcon from 'icons/full-more.svg'
import strokeConnectIcon from 'icons/stroke-connect.svg'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'

import { Card } from '../Card'
import { VenueOfferSteps } from '../VenueOfferSteps/VenueOfferSteps'
import { shouldShowVenueOfferStepsForVenue } from '../venueUtils'

import styles from './Venue.module.scss'

export interface VenueProps {
  offerer?: GetOffererResponseModel | null
  venue: GetOffererVenueResponseModel
  isFirstVenue: boolean
}

export const Venue = ({ offerer, venue, isFirstVenue }: VenueProps) => {
  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )
  const shouldShowVenueOfferSteps = shouldShowVenueOfferStepsForVenue(
    isNewBankDetailsJourneyEnabled,
    venue
  )

  const [prevInitialOpenState, setPrevInitialOpenState] = useState(
    shouldShowVenueOfferSteps
  )
  const [prevOffererId, setPrevOffererId] = useState(offerer?.id)
  const [isToggleOpen, setIsToggleOpen] = useState(shouldShowVenueOfferSteps)
  const { logEvent } = useAnalytics()

  const venueIdTrackParam = {
    venue_id: venue.id,
  }

  if (prevInitialOpenState != shouldShowVenueOfferSteps) {
    setIsToggleOpen(shouldShowVenueOfferSteps)
    setPrevInitialOpenState(shouldShowVenueOfferSteps)
  }

  if (offerer?.id !== prevOffererId) {
    setPrevOffererId(offerer?.id)
  }

  const editVenueLink = `/structures/${offerer?.id}/lieux/${venue.id}?modification`
  const reimbursementSectionLink = `/structures/${offerer?.id}/lieux/${venue.id}?modification#remboursement`
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
                logEvent?.(
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
                viewBox="0 0 16 16"
                src={isToggleOpen ? fullDisclosureOpen : fullDisclosureClose}
              />
              <span>{venueDisplayName}</span>
            </button>
          ) : (
            <div className={styles['venue-name']}>{venueDisplayName}</div>
          )}

          {shouldShowVenueOfferSteps && !venue.isVirtual && (
            <Button
              icon={fullErrorIcon}
              className={styles['needs-payment-icon']}
              variant={ButtonVariant.TERNARY}
              hasTooltip
              onClick={() => {
                setIsToggleOpen((prev) => !prev)
                logEvent?.(
                  VenueEvents.CLICKED_VENUE_ACCORDION_BUTTON,
                  venueIdTrackParam
                )
              }}
            >
              Cliquer pour voir les prochaines étapes
            </Button>
          )}

          {venue.hasVenueProviders && (
            <Tag
              variant={TagVariant.LIGHT_PURPLE}
              className={styles['api-tag']}
            >
              <SvgIcon alt="" src={strokeConnectIcon} />
              API
            </Tag>
          )}
        </h3>

        <div className={styles['button-group']}>
          {/*Delete when WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY is deleted*/}
          {!isNewBankDetailsJourneyEnabled &&
            venue.hasMissingReimbursementPoint &&
            !venue.isVirtual &&
            venue.hasCreatedOffer && (
              <>
                <ButtonLink
                  variant={ButtonVariant.TERNARYPINK}
                  link={{
                    to: reimbursementSectionLink,
                    isExternal: false,
                  }}
                  onClick={() => {
                    logEvent?.(VenueEvents.CLICKED_VENUE_ADD_RIB_BUTTON, {
                      from: location.pathname,
                      ...venueIdTrackParam,
                    })
                  }}
                  icon={fullMoreIcon}
                >
                  Ajouter un RIB
                </ButtonLink>

                <span className={styles['button-group-separator']} />
              </>
            )}

          <ButtonLink
            variant={ButtonVariant.SECONDARY}
            link={{
              to: editVenueLink,
              isExternal: false,
              'aria-label': `Gérer la page de ${venueDisplayName}`,
            }}
            onClick={() =>
              logEvent?.(
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
