import { withLogin } from 'pass-culture-shared'
import React from 'react'

import Main from '../layout/Main'
import MediationManager from '../managers/MediationManager'

const MediationsPage = () => {
  return (
    <Main name="mediations">
      <MediationManager />
    </Main>
  )
}

export default withLogin({ failRedirect: '/connexion' })(MediationsPage)
