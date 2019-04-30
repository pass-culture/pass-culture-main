import classnames from 'classnames'
import PropTypes from 'prop-types'
import React from 'react'
import { NavLink, Route, Switch } from 'react-router-dom'

import MonitoredBookings from './MonitoredBookings'
import MonitoredReimbursements from './MonitoredReimbursements'
import Main from 'components/layout/Main'

const views = [
  {
    label: 'Suivi des réservations',
    name: 'reservations',
    render: () => <MonitoredBookings />,
  },
  {
    label: 'Suivi des remboursements',
    name: 'remboursements',
    render: () => <MonitoredReimbursements />,
  },
]

const Monitoring = ({
  location,
  match: {
    params: { view },
  },
}) => {
  console.log(view)

  return (
    <Main name="monitoring">
      <div className="tabs">
        {views.map(({ label, name, path }) => (
          <NavLink
            className={classnames('tab', {
              selected: view === name,
            })}
            key={name}
            to={`/suivi/${name}`}>
            {label}
          </NavLink>
        ))}
      </div>

      <Switch location={location}>
        {views.map(({ name, render }) => (
          <Route key={name} path={`/suivi/${name}`} render={render} />
        ))}
      </Switch>
    </Main>
  )
}

Monitoring.propTypes = {
  location: PropTypes.object.isRequired,
}

export default Monitoring
