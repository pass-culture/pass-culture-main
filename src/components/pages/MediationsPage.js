import React from 'react'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'


import MediationItem from '../MediationItem'
import withLogin from '../hocs/withLogin'
import withCurrentOccasion from '../hocs/withCurrentOccasion'
import PageWrapper from '../layout/PageWrapper'

const MediationsPage = ({
  isLoading,
  mediations,
  routePath
}) => {
  return (
    <PageWrapper name='mediations' loading={isLoading}>
      <h2 className='title has-text-centered'>
        Vos accroches
      </h2>
      <div className='has-text-right'>
        <NavLink to='/offres'
          className="button is-primary is-outlined">
          Retour
        </NavLink>
      </div>
      <nav className="level is-mobile">
        <NavLink to={`${routePath}/accroches/nouveau`}>
          <button className="button is-primary level-item">
            Nouvel accroche
          </button>
        </NavLink>
      </nav>
      {
        mediations && mediations.map((mediation, index) =>
          <MediationItem
            key={index}
            index={index}
            occasionRoutePath={routePath}
            {...mediation}
          />
        )
      }
    </PageWrapper>
  )
}

export default compose(
  withLogin({ isRequired: true }),
  withCurrentOccasion
)(MediationsPage)
