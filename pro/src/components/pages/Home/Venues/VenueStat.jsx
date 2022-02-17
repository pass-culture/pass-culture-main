import * as PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import { ReactComponent as LoaderSvg } from 'icons/ico-passculture.svg'

export const VenueStat = ({ stat }) => (
  <div className="h-card-col" data-testid="venue-stat">
    {stat.count ? (
      <div className="venue-stat-count">{stat.count}</div>
    ) : (
      <LoaderSvg className="venue-stat-spinner" title="Chargement en cours" />
    )}

    <div>{stat.label}</div>
    <Link className="tertiary-link" to={stat.link}>
      Voir
    </Link>
  </div>
)

VenueStat.propTypes = {
  stat: PropTypes.shape({
    count: PropTypes.string,
    label: PropTypes.string.isRequired,
    link: PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.shape({
        pathname: PropTypes.string,
        state: PropTypes.shape({
          venueId: PropTypes.string,
          statuses: PropTypes.arrayOf(PropTypes.string),
        }),
      }),
    ]).isRequired,
  }).isRequired,
}

export default VenueStat
