import React from 'react'
import { NavLink } from 'react-router-dom'

import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'

const HomePage = ({ user }) => {
  return (
    <PageWrapper key={0} name="home">
      <h1 className='title has-text-centered'>Bienvenue sur l'espace Pro du Pass Culture</h1>

      <div className='content'>
        <p>Ici vous pouvez gérer :</p>
        <ul>
          <li><NavLink to='/etablissements' className='is-primary'>Vos etablissements</NavLink></li>
          <li><NavLink to='/offres' className='is-primary'>Vos offres</NavLink></li>
        </ul>
      </div>
    </PageWrapper>
  )
}

export default withLogin({ isRequired: true })(HomePage)
