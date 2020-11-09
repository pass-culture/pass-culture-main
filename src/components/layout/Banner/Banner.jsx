import PropTypes from 'prop-types'
import React from 'react'

import Icon from 'components/layout/Icon'

const Banner = ({ icon, href, linkTitle, subtitle, type }) => {
  return (
    <div className={`bi-banner ${type}`}>
      <p>
        {subtitle}
      </p>

      <p>
        <a
          className="bi-external-link"
          href={href}
          rel="noopener noreferrer"
          target="_blank"
        >
          <Icon svg={icon} />
          {linkTitle}
        </a>
      </p>
    </div>
  )
}

Banner.defaultProps = {
  icon: 'ico-external-site',
  subtitle: '',
  type: 'attention',
}

Banner.propTypes = {
  href: PropTypes.string.isRequired,
  icon: PropTypes.string,
  linkTitle: PropTypes.string.isRequired,
  subtitle: PropTypes.string,
  type: PropTypes.oneOf(['notification-info', 'attention']),
}

export default Banner
