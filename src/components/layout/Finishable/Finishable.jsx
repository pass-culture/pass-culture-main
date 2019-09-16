import PropTypes from 'prop-types'
import React from 'react'

import Icon from '../Icon/Icon'

const Finishable = ({ isFinished, children }) => {
  if (!isFinished) return children
  return (
    <div className="finishable">
      {children}
      <span className="finish-ribon">
        <span className="finish-ribon-background" />
        <Icon
          alt="Terminé"
          className="finish-ribon-img"
          svg="badge-termine"
        />
      </span>
    </div>
  )
}

Finishable.defaultProps = {
  children: null,
}

Finishable.propTypes = {
  children: PropTypes.node,
  isFinished: PropTypes.bool.isRequired,
}

export default Finishable
