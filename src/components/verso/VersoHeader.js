import React from 'react'
import PropTypes from 'prop-types'

const VersoHeader = React.memo(({ backgroundColor, subtitle, title }) => (
  <div className="verso-header" style={{ backgroundColor }}>
    <h1
      id="verso-offer-name"
      style={{ lineHeight: '2.7rem' }}
      className="fs40 is-medium is-hyphens"
    >
      {title}
    </h1>
    <h2 id="verso-offer-venue" className="fs22 is-normal is-hyphens">
      {subtitle}
    </h2>
  </div>
))

VersoHeader.defaultProps = {}

VersoHeader.propTypes = {
  backgroundColor: PropTypes.string.isRequired,
  subtitle: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
}

export default VersoHeader
