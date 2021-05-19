import * as PropTypes from 'prop-types'
import React, { Fragment, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import Icon from 'components/layout/Icon'
import { BOOKING_STATUS } from 'components/pages/Bookings/BookingsRecapTable/CellsFormatter/utils/bookingStatusConverter'
import { ReactComponent as IcoPlus } from 'icons/ico-plus.svg'
import * as pcapi from 'repository/pcapi/pcapi'

import VenueStat from './VenueStat'

const Venue = ({ id, isVirtual, name, offererId, publicName }) => {
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

  useEffect(() => {
    pcapi.getVenueStats(id).then(stats => {
      setStats({
        activeBookingsQuantity: stats.activeBookingsQuantity.toString(),
        activeOffersCount: stats.activeOffersCount.toString(),
        soldOutOffersCount: stats.soldOutOffersCount.toString(),
        validatedBookingsQuantity: stats.validatedBookingsQuantity.toString(),
      })
    })
  }, [id])

  return (
    <div className="h-section-row nested offerer-venue">
      <div className={`h-card h-card-${isVirtual ? 'primary' : 'secondary'}`}>
        <div className="h-card-inner">
          <div className="h-card-header-row">
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
            {!isVirtual && (
              <Link
                className="tertiary-link"
                to={`/structures/${offererId}/lieux/${id}?modification`}
              >
                <Icon svg="ico-outer-pen" />
                {'Modifier'}
              </Link>
            )}
          </div>
          <div className="venue-stats">
            {venueStatData.map(stat => (
              <Fragment key={stat.label}>
                <VenueStat stat={stat} />
                <div className="separator" />
              </Fragment>
            ))}

            <div className="h-card-col v-add-offer-link">
              <Link
                className="tertiary-link"
                to={`/offres/creation?structure=${offererId}&lieu=${id}`}
              >
                <IcoPlus />
                <div>
                  {isVirtual ? 'Créer une nouvelle offre numérique' : 'Créer une nouvelle offre'}
                </div>
              </Link>
            </div>
          </div>
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
