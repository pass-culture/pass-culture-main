import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import Icon from '../../../../layout/Icon/Icon'

const InternalLink = ({ to, icon, label }) => (
  <Link to={to}>
    <Icon svg={icon} />
    <div className="list-link-label">
      {label}
    </div>
    <Icon svg="ico-next-lightgrey" />
  </Link>
)

InternalLink.propTypes = {
  icon: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  to: PropTypes.string.isRequired,
}

export default InternalLink
