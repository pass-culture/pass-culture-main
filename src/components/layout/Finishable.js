import React from 'react'

import Icon from './Icon'

export default ({ finished, children }) => {
  if (finished) {
    return (
      <div className="finishable">
        {children}
        <Icon svg="badge-termine" className="finish-icon" />
      </div>
    )
  }
  return children
}
