import React from 'react'

import MediationManager from '../MediationManager'
import PageWrapper from '../layout/PageWrapper'
import withLogin from '../hocs/withLogin'

const MediationsPage = () => {
  return (
    <PageWrapper name='mediations'>
      <MediationManager />
    </PageWrapper>
  )
}

export default withLogin({ isRequired: true })(MediationsPage)
