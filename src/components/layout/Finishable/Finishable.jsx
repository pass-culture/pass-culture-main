import PropTypes from 'prop-types'
import React from 'react'

import Icon from '../Icon/Icon'

const Finishable = ({ offerCannotBeBooked, children }) =>
  offerCannotBeBooked ? (
    <div className="finishable">
      {children}
      <Icon
        alt="Réservation finie"
        className="finishable-ribbon-img"
        svg="badge-termine"
      />
    </div>
  ) : (
    children
  )

Finishable.defaultProps = {
  offerCannotBeBooked: false,
}

Finishable.propTypes = {
  children: PropTypes.node.isRequired,
  offerCannotBeBooked: PropTypes.bool,
}

export default Finishable
