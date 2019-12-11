import classnames from 'classnames'
import PropTypes from 'prop-types'
import React from 'react'
import RedirectToMaintenance from './RedirectToMaintenance'

export const App = ({ modalOpen, isMaintenanceActivated, children }) => {
  if (isMaintenanceActivated) {
    return <RedirectToMaintenance />
  } else return (<div className={classnames('app', { 'modal-open': modalOpen })}>
    {children}
  </div>)
}

App.propTypes = {
  children: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  isMaintenanceActivated: PropTypes.bool.isRequired,
  modalOpen: PropTypes.bool.isRequired,
}
