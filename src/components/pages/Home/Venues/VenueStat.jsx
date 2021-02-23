import * as PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

export const VenueStat = ({ stat }) => (
  <div className="h-card-col">
    <span className="venue-stat-amount">
      {stat.amount}
    </span>
    <span className="venue-stat-label">
      {stat.label}
    </span>
    <Link
      className="venue-stat-link tertiary-link"
      to={stat.url}
    >
      {'Voir'}
    </Link>
  </div>
)

VenueStat.propTypes = {
  stat: PropTypes.shape({
    amount: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
    url: PropTypes.string.isRequired,
  }).isRequired,
}

export default VenueStat
