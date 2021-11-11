/*
* @debt directory "Gaël: this file should be migrated within the new directory structure"
*/

import PropTypes from 'prop-types'
import React from 'react'

const InternalBanner = ({ extraClassName, href, linkTitle, subtitle, type }) => {
  return (
    <div className={`bi-banner ${type} ${extraClassName}`}>
      <p>
        {subtitle}
      </p>

      <p>
        <a
          className="bi-link tertiary-link"
          href={href}
        >
          {linkTitle}
        </a>
      </p>
    </div>
  )
}

InternalBanner.defaultProps = {
  extraClassName: '',
  subtitle: '',
  type: 'attention',
}

InternalBanner.propTypes = {
  extraClassName: PropTypes.string,
  href: PropTypes.string.isRequired,
  linkTitle: PropTypes.string.isRequired,
  subtitle: PropTypes.string,
  type: PropTypes.oneOf(['notification-info', 'attention']),
}

export default InternalBanner
