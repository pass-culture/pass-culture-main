import * as PropTypes from 'prop-types'
import React, { Fragment, useEffect, useState } from 'react'

import useActiveFeature from 'components/hooks/useActiveFeature'
import useAnalytics from 'components/hooks/useAnalytics'
import { BOOKING_STATUS } from 'core/Bookings'
import {
  Events,
  OFFER_FORM_HOMEPAGE,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { venueCreateOfferLink } from 'core/Venue/utils'
import { ReactComponent as DownIcon } from 'icons/ico-caret-down.svg'
import { ReactComponent as RightIcon } from 'icons/ico-caret-right.svg'
import { ReactComponent as PenIcon } from 'icons/ico-pen-black.svg'
import { ReactComponent as IcoPlus } from 'icons/ico-plus.svg'
import * as pcapi from 'repository/pcapi/pcapi'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import VenueStat from './VenueStat'

const Venue = ({
  hasBusinessUnit,
  hasReimbursementPoint,
  id,
  isVirtual,
  name,
  offererId,
  publicName,
}) => {
  const [isStatOpen, setIsStatOpen] = useState(false)
  const [isStatLoaded, setIsStatLoaded] = useState(false)
  const [stats, setStats] = useState({
    activeBookingsQuantity: '',
    activeOffersCount: '',
    soldOutOffersCount: '',
    validatedBookingsQuantity: '',
  })
  const { logEvent } = useAnalytics()

  const venueStatData = [
    {
      count: stats.activeOffersCount,
      label: 'Offres publiées',
      link: `/offres?lieu=${id}&statut=active`,
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
    },
    {
      count: stats.soldOutOffersCount,
      label: 'Offres stocks épuisés',
      link: `/offres?lieu=${id}&statut=epuisee`,
    },
  ]

  const isBankInformationWithSiretActive = useActiveFeature(
    'ENFORCE_BANK_INFORMATION_WITH_SIRET'
  )
  const isNewBankInformationActive = useActiveFeature(
    'ENABLE_NEW_BANK_INFORMATIONS_CREATION'
  )

  useEffect(() => {
    if (isStatOpen && !isStatLoaded) {
      // eslint-disable-next-line @typescript-eslint/no-extra-semi
      ;(async () => {
        const stats = await pcapi.getVenueStats(id)
        setStats({
          activeBookingsQuantity: stats.activeBookingsQuantity.toString(),
          activeOffersCount: stats.activeOffersCount.toString(),
          soldOutOffersCount: stats.soldOutOffersCount.toString(),
          validatedBookingsQuantity: stats.validatedBookingsQuantity.toString(),
        })
        setIsStatLoaded(true)
      })()
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

  let editVenueLink = `/structures/${offererId}/lieux/${id}?modification`

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
                onClick={() => setIsStatOpen(prev => !prev)}
              />
              <span className="title-text" title={publicName || name}>
                {publicName || name}
              </span>
            </h3>
            <div className="button-group">
              {((isNewBankInformationActive && !hasReimbursementPoint) ||
                (isBankInformationWithSiretActive && !hasBusinessUnit)) &&
                !isVirtual && (
                  <>
                    <ButtonLink
                      className="add-rib-link tertiary-link"
                      variant={ButtonVariant.TERNARY}
                      link={{
                        to: editVenueLink,
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
              >
                Modifier
              </ButtonLink>
            </div>
          </div>
          {isStatOpen && (
            <div className="venue-stats">
              {venueStatData.map(stat => (
                <Fragment key={stat.label}>
                  <VenueStat stat={stat} />
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
          )}
        </div>
      </div>
    </div>
  )
}

Venue.defaultProps = {
  hasBusinessUnit: false,
  id: '',
  isVirtual: false,
  offererId: '',
  publicName: '',
}

Venue.propTypes = {
  hasBusinessUnit: PropTypes.bool,
  id: PropTypes.string,
  isVirtual: PropTypes.bool,
  name: PropTypes.string.isRequired,
  offererId: PropTypes.string,
  publicName: PropTypes.string,
}

export default Venue
