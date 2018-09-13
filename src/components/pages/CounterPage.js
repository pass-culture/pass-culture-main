import { Icon, withLogin } from 'pass-culture-shared'
import React from 'react'
import { Link } from 'react-router-dom'

import Main from '../layout/Main'

const CounterPage = () => {
  return (
    <Main name="counter">
      {/*
      <div className='section'>
        <h1 className="main-title">Guichet</h1>
        <p className="subtitle">
          Enregistrez les codes de réservations présentés par les porteurs du Pass.
        </p>
      </div>

      <div className='section'>
        <p className="subtitle is-medium has-text-weight-bold">
          Scannez un code-barres, ou saisissez-le ci-dessous:
        </p>
        <FormField
          collectionName='bookings'
          isHorizontal
          name='code'
          type="booking"
        />
      </div>

      <NavLink
        className="button is-primary is-medium is-pulled-right"
        to='/offres'>
        Terminer
      </NavLink>
      */}

      <h1>
        <strong>Page en cours de construction</strong>
      </h1>
      <footer>
        <Link
          to="/accueil"
          className="button is-secondary has-text-weight-light is-italic">
          Revenir à l'accueil
          <Icon svg="ico-next" />
        </Link>
      </footer>
    </Main>
  )
}

export default withLogin({ failRedirect: '/connexion' })(CounterPage)
