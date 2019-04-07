import React from 'react'
import PropTypes from 'prop-types'

const VersoHeader = React.memo(({ backgroundColor, subtitle, title }) => (
  <div
    className="verso-header with-triangle is-relative pc-theme-black py32 px12"
    style={{ backgroundColor }}
  >
    {title && (
      <h1
        id="verso-offer-name"
        style={{ lineHeight: '2.7rem' }}
        className="fs40 is-medium is-hyphens"
      >
        {title}
      </h1>
    )}
    {subtitle && (
      <h2 id="verso-offer-venue" className="fs22 is-normal is-hyphens">
        {subtitle}
      </h2>
    )}
  </div>
))

VersoHeader.defaultProps = {
  subtitle: null,
  title: null,
}

VersoHeader.propTypes = {
  backgroundColor: PropTypes.string.isRequired,
  subtitle: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
}

export default VersoHeader
