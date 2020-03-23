import PropTypes from 'prop-types'
import React from 'react'

import Icon from '../Icon/Icon'

const Finishable = ({ offerCanBeBooked, isBookedByCurrentUser, children }) =>
  offerCanBeBooked || isBookedByCurrentUser ? (
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
  isBookedByCurrentUser: false,
  offerCanBeBooked: true,
}

Finishable.propTypes = {
  children: PropTypes.node.isRequired,
  isBookedByCurrentUser: PropTypes.bool,
  offerCanBeBooked: PropTypes.bool,
}

export default Finishable
