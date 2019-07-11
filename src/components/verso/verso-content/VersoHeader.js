import React from 'react'
import PropTypes from 'prop-types'

const VersoHeader = ({ backgroundColor, subtitle, title }) => (
  <div
    className="verso-header with-triangle is-relative pc-theme-black py32 px12"
    style={{ backgroundColor }}
  >
    {title && (
      <h1
        className="fs40 is-medium is-hyphens"
        id="verso-offer-name"
        style={{ lineHeight: '2.7rem' }}
      >
        {title}
      </h1>
    )}
    {subtitle && (
      <h2
        className="fs22 is-normal is-hyphens"
        id="verso-offer-venue"
      >
        {subtitle}
      </h2>
    )}
  </div>
)

VersoHeader.defaultProps = {
  subtitle: null,
  title: null,
}

VersoHeader.propTypes = {
  backgroundColor: PropTypes.string.isRequired,
  subtitle: PropTypes.string,
  title: PropTypes.string,
}

export default VersoHeader
