import React from 'react'

import { Icon } from 'pass-culture-shared'

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
