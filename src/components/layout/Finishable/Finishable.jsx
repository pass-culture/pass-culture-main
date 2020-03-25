import PropTypes from 'prop-types'
import React from 'react'

import Icon from '../Icon/Icon'

const Finishable = ({ offerCanBeOrIsBooked, children }) =>
  offerCanBeOrIsBooked ? (
    children
  ) : (
    <div className="finishable">
      {children}
      <Icon
        alt="Réservation finie"
        className="finishable-ribbon-img"
        svg="badge-termine"
      />
    </div>
  )

Finishable.defaultProps = {
  offerCanBeOrIsBooked: true,
}

Finishable.propTypes = {
  children: PropTypes.node.isRequired,
  offerCanBeOrIsBooked: PropTypes.bool,
}

export default Finishable
