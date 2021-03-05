import * as PropTypes from 'prop-types'
import React, { Fragment, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import Icon from 'components/layout/Icon'
import { ReactComponent as IcoPlus } from 'icons/ico-plus.svg'
import * as pcapi from 'repository/pcapi/pcapi'

import VenueStat from './VenueStat'

const Venue = ({ id, isVirtual, name, offererId, publicName }) => {
  const [stats, setStats] = useState({
    activeBookingsCount: '',
    activeOffersQuantity: '',
  })

  const venueStatData = [
    {
      count: stats.activeOffersQuantity,
      label: 'Offres actives',
      url: `/offres?lieu=${id}&statut=active`,
    },
    {
      count: stats.activeBookingsQuantity,
      label: 'Réservations en cours',
      url: `/reservations`,
    },
    {
      count: stats.usedBookingsQuantity,
      label: 'Réservations validées',
      url: `/reservations`,
    },
    {
      count: '- -',
      label: 'Offres stocks épuisés',
      url: `/offres?lieu=${id}&statut=epuisee`,
    },
  ]

  useEffect(() => {
    pcapi.getVenueStats(id).then(stats => {
      setStats({
        activeBookingsQuantity: stats.activeBookingsQuantity.toString(),
        activeOffersQuantity: stats.activeOffersQuantity.toString(),
        usedBookingsQuantity: stats.usedBookingsQuantity.toString(),
      })
    })
  }, [id])

  return (
    <div className="h-section-row nested">
      <div className={`h-card h-card-${isVirtual ? 'primary' : 'secondary'}`}>
        <div className="h-card-inner">
          <div className="h-card-header-row">
            <h3 className="h-card-title">
              <Icon
                className="h-card-title-ico"
                svg={isVirtual ? 'ico-screen-play' : 'ico-box'}
              />
              {publicName || name}
            </h3>
            {!isVirtual && (
              <Link
                className="tertiary-link"
                to={`/structures/${offererId}/lieux/${id}`}
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
                <IcoPlus aria-hidden />
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
