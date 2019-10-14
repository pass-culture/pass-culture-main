import PropTypes from 'prop-types'
import React from 'react'

import Icon from '../Icon/Icon'

const Finishable = ({ isNotBookable, children }) =>
  isNotBookable ? (
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
  isNotBookable: false,
}

Finishable.propTypes = {
  children: PropTypes.node.isRequired,
  isNotBookable: PropTypes.bool,
}

export default Finishable
