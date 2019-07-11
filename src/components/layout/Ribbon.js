import React from 'react'
import PropTypes from 'prop-types'

const Ribbon = ({ label, placement, type }) => (
  <div className={`ribbon ribbon-${type} ribbon-${placement}`}>
    <span>{label}</span>
  </div>
)

Ribbon.defaultProps = {
  label: 'Annulé',
  placement: 'right',
  type: 'cancelled',
}

Ribbon.propTypes = {
  label: PropTypes.string,
  placement: PropTypes.string,
  type: PropTypes.oneOf(['cancelled', 'today', 'tomorrow']),
}

export default Ribbon
