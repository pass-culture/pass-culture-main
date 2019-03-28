import React from 'react'
import PropTypes from 'prop-types'

import { Icon } from 'pass-culture-shared'

const Finishable = ({ finished, children }) => {
  if (!finished) return children
  return (
    <div className="finishable">
      {children}
      <Icon svg="badge-termine" className="finish-icon" alt="Terminé" />
    </div>
  )
}

Finishable.defaultProps = {
  finished: false,
}

Finishable.propTypes = {
  children: PropTypes.node.isRequired,
  finished: PropTypes.bool,
}

export default Finishable
