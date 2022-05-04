import React from 'react'
import { useHistory, useLocation } from 'react-router-dom'

// use to update react-router-dom to v6 before all class components
// are migrated to functional component
export const withRouter = Component => {
  return props => (
    <Component {...props} history={useHistory()} location={useLocation()} />
  )
}
