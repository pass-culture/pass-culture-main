import PropTypes from 'prop-types'
import React from 'react'

import Icon from '../../../layout/Icon/Icon'

const ExternalLink = ({ href, icon, title, label, rel, target }) => (
  <a
    href={href}
    rel={rel}
    target={target}
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
  rel: PropTypes.string,
  target: PropTypes.string,
  title: PropTypes.string.isRequired,
}

ExternalLink.defaultProps = {
  rel: 'noopener noreferrer',
  target: '_blank',
}

export default ExternalLink
