import PropTypes from 'prop-types'
import React from 'react'

import Icon from './Icon'

const Finishable = ({ finished, children }) => {
  if (!finished) return children
  return (
    <div className="finishable">
      {children}
      <span className="finish-ribon">
        <span className="finish-ribon-background" />
        <Icon className="finish-ribon-img" svg="badge-termine" alt="Terminé" />
      </span>
    </div>
  )
}

Finishable.defaultProps = {
  children: null,
}

Finishable.propTypes = {
  children: PropTypes.node,
  finished: PropTypes.bool.isRequired,
}

export default Finishable
