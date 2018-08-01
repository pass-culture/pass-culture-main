import { Icon } from 'pass-culture-shared'
import React from 'react'

export default ({ finished, children }) => {
  if (finished) {
    return (
      <div className="finishable">
        {children}
        <Icon svg="badge-termine" className="finish-icon" alt="Terminé" />
      </div>
    )
  }
  return children
}
