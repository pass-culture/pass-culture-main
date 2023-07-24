import cn from 'classnames'
import { addDays, isBefore } from 'date-fns'
import React, { Fragment, useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import { DMSApplicationForEAC, DMSApplicationstatus } from 'apiClient/v1'
import { BOOKING_STATUS } from 'core/Bookings/constants'
import {
  Events,
  OFFER_FORM_HOMEPAGE,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
  VenueEvents,
} from 'core/FirebaseEvents/constants'
import { venueCreateOfferLink } from 'core/Venue/utils'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import fullDisclosureClose from 'icons/full-disclosure-close.svg'
import fullDisclosureOpen from 'icons/full-disclosure-open.svg'
import fullEditIcon from 'icons/full-edit.svg'
import fullErrorIcon from 'icons/full-error.svg'
import fullMoreIcon from 'icons/full-more.svg'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Spinner from 'ui-kit/Spinner/Spinner'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { VenueOfferSteps } from '../VenueOfferSteps'

import VenueStat from './VenueStat'

export interface VenueProps {
  hasMissingReimbursementPoint?: boolean
  venueId: number
  isVirtual?: boolean
  name: string
  offererId: number
  publicName?: string | null
  hasCreatedOffer?: boolean
  dmsInformations?: DMSApplicationForEAC | null
  hasAdageId?: boolean
  adageInscriptionDate?: string | null
  hasPendingBankInformationApplication?: boolean | null
  demarchesSimplifieesApplicationId?: number | null
}

const Venue = ({
  hasMissingReimbursementPoint = false,
  venueId,
  isVirtual = false,
  name,
  offererId,
  publicName,
  hasCreatedOffer,
  dmsInformations,
  hasAdageId,
  adageInscriptionDate,
  demarchesSimplifieesApplicationId,
  hasPendingBankInformationApplication = false,
}: VenueProps) => {
  const isCollectiveDmsTrackingActive = useActiveFeature(
    'WIP_ENABLE_COLLECTIVE_DMS_TRACKING'
  )
  const hasAdageIdForMoreThan30Days =
    hasAdageId &&
    !!adageInscriptionDate &&
    isBefore(new Date(adageInscriptionDate), addDays(new Date(), -30))

  const hasRefusedApplicationForMoreThan30Days =
    (dmsInformations?.state == DMSApplicationstatus.REFUSE ||
      dmsInformations?.state == DMSApplicationstatus.SANS_SUITE) &&
    dmsInformations.processingDate &&
    isBefore(
      new Date(dmsInformations?.processingDate),
      addDays(new Date(), -30)
    )

  const shouldDisplayEACInformationSection =
    isCollectiveDmsTrackingActive &&
    Boolean(dmsInformations) &&
    !hasAdageIdForMoreThan30Days &&
    !hasRefusedApplicationForMoreThan30Days

  const initialOpenState =
    shouldDisplayEACInformationSection ||
    !hasCreatedOffer ||
    hasPendingBankInformationApplication

  const [prevInitialOpenState, setPrevInitialOpenState] =
    useState(initialOpenState)
  const [prevOffererId, setPrevOffererId] = useState(offererId)
  const [isStatOpen, setIsStatOpen] = useState(initialOpenState)
  const [isStatLoaded, setIsStatLoaded] = useState(false)
  const INITIAL_STATS_VALUE = {
    activeBookingsQuantity: '',
    activeOffersCount: '',
    soldOutOffersCount: '',
    validatedBookingsQuantity: '',
  }
  const [stats, setStats] = useState(INITIAL_STATS_VALUE)
  const { logEvent } = useAnalytics()

  const venueIdTrackParam = {
    venue_id: venueId,
  }

  const venueStatData = [
    {
      count: stats.activeOffersCount,
      label: 'Offres publiées',
      link: {
        pathname: `/offres?lieu=${venueId}&statut=active`,
      },
      onClick: () => {
        logEvent?.(
          VenueEvents.CLICKED_VENUE_PUBLISHED_OFFERS_LINK,
          venueIdTrackParam
        )
      },
    },
    {
      count: stats.activeBookingsQuantity,
      label: 'Réservations en cours',
      link: {
        pathname: `/reservations?page=1&offerVenueId=${venueId}`,
        state: {
          venueId: venueId,
          statuses: [
            BOOKING_STATUS.CANCELLED,
            BOOKING_STATUS.CONFIRMED,
            BOOKING_STATUS.REIMBURSED,
            BOOKING_STATUS.VALIDATED,
          ],
        },
      },
      onClick: () => {
        logEvent?.(
          VenueEvents.CLICKED_VENUE_ACTIVE_BOOKINGS_LINK,
          venueIdTrackParam
        )
      },
    },
    {
      count: stats.validatedBookingsQuantity,
      label: 'Réservations validées',
      link: {
        pathname: `/reservations?page=1&bookingStatusFilter=validated&offerVenueId=${venueId}`,
        state: {
          statuses: [BOOKING_STATUS.BOOKED, BOOKING_STATUS.CANCELLED],
        },
      },
      onClick: () => {
        logEvent?.(
          VenueEvents.CLICKED_VENUE_VALIDATED_RESERVATIONS_LINK,
          venueIdTrackParam
        )
      },
    },
    {
      count: stats.soldOutOffersCount,
      label: 'Offres stocks épuisés',
      link: {
        pathname: `/offres?lieu=${venueId}&statut=epuisee`,
      },
      onClick: () => {
        logEvent?.(
          VenueEvents.CLICKED_VENUE_EMPTY_STOCK_LINK,
          venueIdTrackParam
        )
      },
    },
  ]

  if (prevInitialOpenState != initialOpenState) {
    setIsStatOpen(initialOpenState)
    setPrevInitialOpenState(initialOpenState)
  }

  if (offererId !== prevOffererId) {
    setPrevOffererId(offererId)
    if (stats !== INITIAL_STATS_VALUE) {
      setIsStatOpen(false)
      setIsStatLoaded(false)
      setStats(INITIAL_STATS_VALUE)
    }
  }

  useEffect(() => {
    async function updateStats() {
      const stats = await api.getVenueStats(venueId)
      setStats({
        activeBookingsQuantity: stats.activeBookingsQuantity.toString(),
        activeOffersCount: stats.activeOffersCount.toString(),
        soldOutOffersCount: stats.soldOutOffersCount.toString(),
        validatedBookingsQuantity: stats.validatedBookingsQuantity.toString(),
      })
      setIsStatLoaded(true)
    }
    if (isStatOpen && !isStatLoaded) {
      updateStats()
    }
  }, [venueId, isStatOpen, isStatLoaded, initialOpenState])

  const editVenueLink = `/structures/${offererId}/lieux/${venueId}?modification`
  const reimbursementSectionLink = `/structures/${offererId}/lieux/${venueId}?modification#remboursement`
  return (
    <div
      className="h-section-row nested offerer-venue"
      data-testid="venue-wrapper"
    >
      <div
        className={cn(
          `h-card`,
          { 'h-card-primary': isVirtual },
          { 'h-card-secondary': !isVirtual }
        )}
      >
        <div className="h-card-inner">
          <div
            className={cn('h-card-header-row', {
              'h-card-is-open': isStatOpen,
            })}
          >
            <h3 className="h-card-title">
              <button
                className="h-card-title h-card-title-button"
                type="button"
                title={`${
                  isStatOpen ? 'Masquer' : 'Afficher'
                } les statistiques de ${publicName || name}`}
                onClick={() => {
                  setIsStatOpen(prev => !prev)
                  logEvent?.(
                    VenueEvents.CLICKED_VENUE_ACCORDION_BUTTON,
                    venueIdTrackParam
                  )
                }}
              >
                <SvgIcon
                  alt="icon"
                  className="h-card-title-ico align-baseline"
                  viewBox="0 0 16 16"
                  src={isStatOpen ? fullDisclosureOpen : fullDisclosureClose}
                />
                <span className="align-baseline">{publicName || name}</span>
              </button>
              {initialOpenState && !isVirtual && (
                <Button
                  icon={fullErrorIcon}
                  className="needs-payment-icon"
                  variant={ButtonVariant.TERNARY}
                  hasTooltip
                  onClick={() => {
                    setIsStatOpen(prev => !prev)
                    logEvent?.(
                      VenueEvents.CLICKED_VENUE_ACCORDION_BUTTON,
                      venueIdTrackParam
                    )
                  }}
                >
                  Cliquer pour voir les prochaines étapes
                </Button>
              )}
            </h3>
            <div className="button-group">
              {hasMissingReimbursementPoint &&
                !isVirtual &&
                hasCreatedOffer && (
                  <>
                    <ButtonLink
                      className="add-rib-link tertiary-link"
                      variant={ButtonVariant.TERNARY}
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
                    <span className="button-group-separator" />
                  </>
                )}
              <ButtonLink
                variant={ButtonVariant.TERNARY}
                link={{
                  to: editVenueLink,
                  isExternal: false,
                }}
                icon={fullEditIcon}
                onClick={() =>
                  logEvent?.(
                    VenueEvents.CLICKED_VENUE_PUBLISHED_OFFERS_LINK,
                    venueIdTrackParam
                  )
                }
              >
                Éditer le lieu
              </ButtonLink>
            </div>
          </div>
          {isStatOpen && (
            <>
              {isStatLoaded ? (
                <>
                  <VenueOfferSteps
                    venueId={venueId}
                    hasVenue={true}
                    offererId={offererId}
                    hasCreatedOffer={hasCreatedOffer}
                    hasMissingReimbursementPoint={hasMissingReimbursementPoint}
                    hasAdageId={hasAdageId}
                    shouldDisplayEACInformationSection={
                      shouldDisplayEACInformationSection
                    }
                    hasPendingBankInformationApplication={
                      hasPendingBankInformationApplication
                    }
                    demarchesSimplifieesApplicationId={
                      demarchesSimplifieesApplicationId
                    }
                  />

                  <div className="venue-stats">
                    {venueStatData.map(stat => (
                      <Fragment key={stat.label}>
                        <VenueStat {...stat} />
                      </Fragment>
                    ))}
                    <div className="h-card-col v-add-offer-link">
                      <ButtonLink
                        variant={ButtonVariant.TERNARY}
                        link={{
                          to: venueCreateOfferLink(
                            offererId,
                            venueId,
                            isVirtual
                          ),
                          isExternal: false,
                        }}
                        icon={fullMoreIcon}
                        onClick={() =>
                          logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
                            from: OFFER_FORM_NAVIGATION_IN.HOME,
                            to: OFFER_FORM_HOMEPAGE,
                            used: isVirtual
                              ? OFFER_FORM_NAVIGATION_MEDIUM.HOME_VIRTUAL_LINK
                              : OFFER_FORM_NAVIGATION_MEDIUM.HOME_LINK,
                            isEdition: false,
                          })
                        }
                      >
                        {isVirtual
                          ? 'Créer une nouvelle offre numérique'
                          : 'Créer une nouvelle offre'}
                      </ButtonLink>
                    </div>
                  </div>
                </>
              ) : (
                <Spinner />
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default Venue
