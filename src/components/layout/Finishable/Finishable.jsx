import PropTypes from 'prop-types'
import React from 'react'

import Icon from '../Icon/Icon'

const Finishable = ({ offerCanBeBooked, children }) =>
  offerCanBeBooked ? (
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
  offerCanBeBooked: true,
}

Finishable.propTypes = {
  children: PropTypes.node.isRequired,
  offerCanBeBooked: PropTypes.bool,
}

export default Finishable
