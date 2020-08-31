import PropTypes from 'prop-types'
import React from 'react'

import Icon from '../../../../layout/Icon/Icon'

const ExternalLink = ({ href, icon, title, label }) => (
  <a
    href={href}
    rel="noopener noreferrer"
    target="_blank"
    title={title}
  >
    <Icon svg={icon} />
    <div className="list-link-label">
      {label}
    </div>
    <Icon svg="ico-next-lightgrey" />
  </a>
)

ExternalLink.propTypes = {
  href: PropTypes.string.isRequired,
  icon: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
}

export default ExternalLink
