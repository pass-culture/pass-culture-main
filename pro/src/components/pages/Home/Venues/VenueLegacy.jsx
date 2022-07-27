import * as PropTypes from 'prop-types'
import * as pcapi from 'repository/pcapi/pcapi'

import React, { Fragment, useEffect, useState } from 'react'

import { BOOKING_STATUS } from 'core/Bookings'
import { ReactComponent as IcoPlus } from 'icons/ico-plus.svg'
import Icon from 'components/layout/Icon'
import { Link } from 'react-router-dom'
import VenueStat from './VenueStat'
import useActiveFeature from 'components/hooks/useActiveFeature'
import { venueCreateOfferLink } from 'core/Venue/utils'

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
              <button
                className="tertiary-button"
                onClick={() => setIsStatOpen(prev => !prev)}
                title={isStatOpen ? 'Masquer' : 'Afficher'}
                type="button"
              >
                <Icon
                  className="h-card-title-ico"
                  svg={isStatOpen ? 'ico-caret-down' : 'ico-caret-right'}
                />
              </button>
              <span className="title-text" title={publicName || name}>
                {publicName || name}
              </span>
            </h3>
            <div className="button-group">
              {(isNewBankInformationActive ||
                isBankInformationWithSiretActive) &&
                !hasReimbursementPoint &&
                !hasBusinessUnit &&
                !isVirtual && (
                  <>
                    <Link
                      className="add-rib-link tertiary-link"
                      to={editVenueLink}
                    >
                      <IcoPlus />
                      Ajouter un RIB
                    </Link>
                    <span className="button-group-separator" />
                  </>
                )}
              <Link className="tertiary-link" to={editVenueLink}>
                <Icon svg="ico-outer-pen" />
                Modifier
              </Link>
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
                <Link
                  className="tertiary-link"
                  to={venueCreateOfferLink(offererId, id, isVirtual)}
                >
                  <IcoPlus />
                  <div>
                    {isVirtual
                      ? 'Créer une nouvelle offre numérique'
                      : 'Créer une nouvelle offre'}
                  </div>
                </Link>
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
