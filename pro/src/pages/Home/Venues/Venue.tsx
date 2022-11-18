import React, { Fragment, useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import { BOOKING_STATUS } from 'core/Bookings'
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
import { ReactComponent as DownIcon } from 'icons/ico-caret-down.svg'
import { ReactComponent as RightIcon } from 'icons/ico-caret-right.svg'
import { ReactComponent as PenIcon } from 'icons/ico-pen-black.svg'
import { ReactComponent as IcoPlus } from 'icons/ico-plus.svg'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Spinner from 'ui-kit/Spinner/Spinner'

import VenueStat from './VenueStat'

export interface IVenueProps {
  hasBusinessUnit?: boolean
  hasMissingReimbursementPoint?: boolean
  id: string
  isVirtual?: boolean
  name: string
  offererId: string
  publicName?: string
}

const Venue = ({
  hasBusinessUnit = false,
  hasMissingReimbursementPoint = false,
  id,
  isVirtual = false,
  name,
  offererId,
  publicName,
}: IVenueProps) => {
  const [isStatOpen, setIsStatOpen] = useState(false)
  const [isStatLoaded, setIsStatLoaded] = useState(false)
  const [stats, setStats] = useState({
    activeBookingsQuantity: '',
    activeOffersCount: '',
    soldOutOffersCount: '',
    validatedBookingsQuantity: '',
  })
  const { logEvent } = useAnalytics()

  const venueIdTrackParam = {
    venue_id: id,
  }

  const venueStatData = [
    {
      count: stats.activeOffersCount,
      label: 'Offres publiées',
      link: {
        pathname: `/offres?lieu=${id}&statut=active`,
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
        pathname: `/reservations?page=1&offerVenueId=${id}`,
        state: {
          venueId: id,
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
        pathname: `/reservations?page=1&bookingStatusFilter=validated&offerVenueId=${id}`,
        state: {
          venueId: id,
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
        pathname: `/offres?lieu=${id}&statut=epuisee`,
      },
      onClick: () => {
        logEvent?.(
          VenueEvents.CLICKED_VENUE_EMPTY_STOCK_LINK,
          venueIdTrackParam
        )
      },
    },
  ]

  const isBankInformationWithSiretActive = useActiveFeature(
    'ENFORCE_BANK_INFORMATION_WITH_SIRET'
  )
  const isNewBankInformationActive = useActiveFeature(
    'ENABLE_NEW_BANK_INFORMATIONS_CREATION'
  )

  useEffect(() => {
    async function updateStats() {
      const stats = await api.getVenueStats(id)
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
  }, [id, isStatOpen, isStatLoaded])

  useEffect(() => {
    setIsStatOpen(false)
    setIsStatLoaded(false)
    setStats({
      activeBookingsQuantity: '',
      activeOffersCount: '',
      soldOutOffersCount: '',
      validatedBookingsQuantity: '',
    })
  }, [offererId])

  const editVenueLink = `/structures/${offererId}/lieux/${id}?modification`
  const reimbursementSectionLink = `/structures/${offererId}/lieux/${id}?modification#remboursement`

  return (
    <div
      className="h-section-row nested offerer-venue"
      data-testid="venue-wrapper"
    >
      <div className={`h-card h-card-${isVirtual ? 'primary' : 'secondary'}`}>
        <div className="h-card-inner">
          <div
            className={`h-card-header-row ${
              isStatOpen ? 'h-card-is-open' : ''
            }`}
          >
            <h3 className="h-card-title">
              <Button
                className="h-card-title-ico"
                variant={ButtonVariant.TERNARY}
                Icon={isStatOpen ? DownIcon : RightIcon}
                type="button"
                title={isStatOpen ? 'Masquer' : 'Afficher'}
                onClick={() => {
                  setIsStatOpen(prev => !prev)
                  logEvent?.(
                    VenueEvents.CLICKED_VENUE_ACCORDION_BUTTON,
                    venueIdTrackParam
                  )
                }}
              />
              <a
                className="title-text"
                title={publicName || name}
                href={editVenueLink}
              >
                {publicName || name}
              </a>
            </h3>
            <div className="button-group">
              {((isNewBankInformationActive && hasMissingReimbursementPoint) ||
                (isBankInformationWithSiretActive && !hasBusinessUnit)) &&
                !isVirtual && (
                  <>
                    <ButtonLink
                      className="add-rib-link tertiary-link"
                      variant={ButtonVariant.TERNARY}
                      link={{
                        to: reimbursementSectionLink,
                        isExternal: false,
                      }}
                      Icon={IcoPlus}
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
                Icon={PenIcon}
                onClick={() =>
                  logEvent?.(
                    VenueEvents.CLICKED_VENUE_PUBLISHED_OFFERS_LINK,
                    venueIdTrackParam
                  )
                }
              >
                Modifier
              </ButtonLink>
            </div>
          </div>
          {isStatOpen &&
            (isStatLoaded ? (
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
                      to: venueCreateOfferLink(offererId, id, isVirtual),
                      isExternal: false,
                    }}
                    Icon={IcoPlus}
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
                    <div>
                      {isVirtual
                        ? 'Créer une nouvelle offre numérique'
                        : 'Créer une nouvelle offre'}
                    </div>
                  </ButtonLink>
                </div>
              </div>
            ) : (
              <Spinner />
            ))}
        </div>
      </div>
    </div>
  )
}

export default Venue
