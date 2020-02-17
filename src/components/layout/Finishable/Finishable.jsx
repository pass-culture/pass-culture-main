import PropTypes from 'prop-types'
import React from 'react'

import Icon from '../Icon/Icon'

const Finishable = ({ offerIsNoLongerBookable, children }) =>
  offerIsNoLongerBookable ? (
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
  offerIsNoLongerBookable: false,
}

Finishable.propTypes = {
  children: PropTypes.node.isRequired,
  offerIsNoLongerBookable: PropTypes.bool,
}

export default Finishable
