import React from 'react'
import { NavLink } from 'react-router-dom'

import FormField from '../layout/FormField'
import PageWrapper from '../layout/PageWrapper'

const CounterPage = ({}) => {
  return (
    <PageWrapper
      name='counter'
    >
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

    </PageWrapper>
  )
}

export default CounterPage
