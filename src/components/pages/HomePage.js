import React from 'react'
import { NavLink } from 'react-router-dom'

import OfferersList from '../OfferersList'
import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'
import SignoutButton from '../layout/SignoutButton'

const HomePage = ({ user }) => {
  return (
    <PageWrapper key={0} name="home">
      <h1 className='title has-text-centered'>Bienvenue sur l'espace Pro du Pass Culture</h1>

      <div className='content'>
        <p>Ici vous pouvez gérer :</p>
        <ul>
          <li><NavLink to='/offreurs' className='is-primary'>Vos lieux</NavLink></li>
          <li><NavLink to='/offres' className='is-primary'>Vos offres</NavLink></li>
        </ul>
      </div>
    </PageWrapper>
  )
}

export default withLogin({ isRequired: true })(HomePage)
