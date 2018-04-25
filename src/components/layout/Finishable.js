import React from 'react'
import Icon from '../layout/Icon'

export default ({ finished, children }) => {
  if (finished) {
    return (
      <div className="finishable">
        <Icon svg="badge-termine" className="finish-icon" />
        {children}
      </div>
    )
  }
  return children
}
