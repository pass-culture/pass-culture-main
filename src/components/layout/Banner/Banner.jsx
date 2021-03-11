import PropTypes from 'prop-types'
import React from 'react'

import Icon from 'components/layout/Icon'
import { requiredIfComponentHasProp } from 'utils/propTypes'

const Banner = ({ icon, href, linkTitle, message, type }) => {
  return (
    <div className={`bi-banner ${type}`}>
      <p>
        {message}
      </p>

      {href && linkTitle && (
        <p>
          <a
            className="bi-link tertiary-link"
            href={href}
            rel="noopener noreferrer"
            target="_blank"
          >
            <Icon svg={icon} />
            {linkTitle}
          </a>
        </p>
      )}
    </div>
  )
}

Banner.defaultProps = {
  href: null,
  icon: 'ico-external-site',
  linkTitle: null,
  message: '',
  type: 'attention',
}

Banner.propTypes = {
  href: requiredIfComponentHasProp('linkTitle', 'string'),
  icon: PropTypes.string,
  linkTitle: requiredIfComponentHasProp('href', 'string'),
  message: PropTypes.string,
  type: PropTypes.oneOf(['notification-info', 'attention']),
}

export default Banner
