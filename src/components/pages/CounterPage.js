import React from 'react'
import { Link } from 'react-router-dom'

import Icon from '../layout/Icon'
// import FormField from '../layout/FormField'
import PageWrapper from '../layout/PageWrapper'

const CounterPage = () => {
  return (
    <PageWrapper
      name='counter'
    >
      {
      /*
      <div className='section hero'>
        <h1 className="pc-title">Guichet</h1>
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
      */
      }

      <h1>
        <strong>Page en cours de construction</strong>
      </h1>
      <footer>
        <Link
          to="/accueil"
          className="button is-secondary has-text-weight-light is-italic"
        >
          Revenir à l'accueil
          <Icon svg="ico-next" />
        </Link>
      </footer>

    </PageWrapper>
  )
}

export default CounterPage
