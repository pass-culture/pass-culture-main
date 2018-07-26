import React from 'react'

import MediationManager from '../MediationManager'
import PageWrapper from '../layout/PageWrapper'

const MediationsPage = () => {
  return (
    <PageWrapper name='mediations'>
      <MediationManager />
    </PageWrapper>
  )
}

export default MediationsPage
