import PropTypes from 'prop-types'
import React from 'react'

import Icon from '../Icon/Icon'

const Finishable = ({ shouldDisplayFinishedBanner, children }) =>
  shouldDisplayFinishedBanner ? (
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
  shouldDisplayFinishedBanner: false,
}

Finishable.propTypes = {
  children: PropTypes.node.isRequired,
  shouldDisplayFinishedBanner: PropTypes.bool,
}

export default Finishable
