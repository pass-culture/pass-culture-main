import PropTypes from 'prop-types'
import React from 'react'

import Icon from 'components/layout/Icon'

const Banner = ({ subtitle, href, linkTitle, icon }) => {
  return (
    <div className="bi-banner">
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
          <Icon
            alt=""
            svg={icon}
          />
          {linkTitle}
        </a>
      </p>
    </div>
  )
}

Banner.defaultProps = {
  icon: 'ico-external-site',
}

Banner.propTypes = {
  href: PropTypes.string.isRequired,
  icon: PropTypes.string,
  linkTitle: PropTypes.string.isRequired,
  subtitle: PropTypes.string.isRequired,
}

export default Banner
