import PropTypes from 'prop-types'
import React from 'react'

const InternalBanner = ({ href, linkTitle, subtitle, type }) => {
  return (
    <div className={`bi-banner ${type}`}>
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
  subtitle: '',
  type: 'attention',
}

InternalBanner.propTypes = {
  href: PropTypes.string.isRequired,
  linkTitle: PropTypes.string.isRequired,
  subtitle: PropTypes.string,
  type: PropTypes.oneOf(['notification-info', 'attention']),
}

export default InternalBanner
