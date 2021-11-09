/*
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 */

import * as PropTypes from 'prop-types'
import React, { Fragment, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import useActiveFeature from 'components/hooks/useActiveFeature'
import Icon from 'components/layout/Icon'
import { BOOKING_STATUS } from 'components/pages/Bookings/BookingsRecapTable/CellsFormatter/utils/bookingStatusConverter'
import { ReactComponent as IcoPlus } from 'icons/ico-plus.svg'
import * as pcapi from 'repository/pcapi/pcapi'

import { ReactComponent as ClosedEyeSvg } from '../Offerers/assets/ico-eye-close.svg'
import { ReactComponent as OpenedEyeSvg } from '../Offerers/assets/ico-eye-open.svg'

import VenueStat from './VenueStat'

const Venue = ({ id, isVirtual, name, offererId, publicName }) => {
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
      label: 'Offres actives',
      link: `/offres?lieu=${id}&statut=active`,
    },
    {
      count: stats.activeBookingsQuantity,
      label: 'Réservations en cours',
      link: {
        pathname: '/reservations',
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
        pathname: '/reservations',
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

  const isVenueV2Enabled = useActiveFeature('ENABLE_NEW_VENUE_PAGES')
  const isBankInformationWithSiretActive = useActiveFeature('ENFORCE_BANK_INFORMATION_WITH_SIRET')

  useEffect(() => {
    if (isStatOpen && !isStatLoaded) {
      (async () => {
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

  let editVenueLink = `/structures/${offererId}/lieux/${id}`

  if (!isVenueV2Enabled) {
    editVenueLink += '?modification'
  }

  return (
    <div
      className="h-section-row nested offerer-venue"
      data-testid="venue-wrapper"
    >
      <div className={`h-card h-card-${isVirtual ? 'primary' : 'secondary'}`}>
        <div className="h-card-inner">
          <div className={`h-card-header-row ${isStatOpen ? 'h-card-is-open' : ''}`}>
            <h3 className="h-card-title">
              <Icon
                className="h-card-title-ico"
                svg={isVirtual ? 'ico-screen-play' : 'ico-box'}
              />
              <span
                className="title-text"
                title={publicName || name}
              >
                {publicName || name}
              </span>
            </h3>
            <div className="button-group">
              <button
                className={`tertiary-button ${isStatOpen ? 'od-primary' : ''}`}
                onClick={() => setIsStatOpen(prev => !prev)}
                type="button"
              >
                {isStatOpen ? (
                  <>
                    <ClosedEyeSvg />
                    {' '}
                    Masquer
                  </>
                ) : (
                  <>
                    <OpenedEyeSvg />
                    {' '}
                    Afficher
                  </>
                )}
              </button>
              {(!isVirtual || isBankInformationWithSiretActive) && (
                <>
                  <span className="button-group-separator" />
                  <Link
                    className="tertiary-link"
                    to={editVenueLink}
                  >
                    <Icon svg="ico-outer-pen" />
                    Modifier
                  </Link>
                </>
              )}
            </div>
          </div>
          {isStatOpen && (
            <>
              <div className="od-separator horizontal" />
              <div className="venue-stats">
                {venueStatData.map(stat => (
                  <Fragment key={stat.label}>
                    <VenueStat stat={stat} />
                  </Fragment>
                ))}
                <div className="h-card-col v-add-offer-link">
                  <Link
                    className="tertiary-link"
                    to={`/offres/creation?structure=${offererId}&lieu=${id}`}
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
            </>
          )}
        </div>
      </div>
    </div>
  )
}

Venue.defaultProps = {
  id: '',
  isVirtual: false,
  offererId: '',
  publicName: '',
}

Venue.propTypes = {
  id: PropTypes.string,
  isVirtual: PropTypes.bool,
  name: PropTypes.string.isRequired,
  offererId: PropTypes.string,
  publicName: PropTypes.string,
}

export default Venue
