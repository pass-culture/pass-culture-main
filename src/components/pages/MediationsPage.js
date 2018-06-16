import React from 'react'
import { compose } from 'redux'

import MediationManager from '../MediationManager'
import PageWrapper from '../layout/PageWrapper'
import withCurrentOccasion from '../hocs/withCurrentOccasion'
import withLogin from '../hocs/withLogin'

const MediationsPage = ({
  currentMediations,
  isLoading
}) => {
  return (
    <PageWrapper name='mediations' loading={isLoading}>
      <MediationManager mediations={currentMediations} />
    </PageWrapper>
  )
}

export default compose(
  withLogin({ isRequired: true }),
  withCurrentOccasion
)(MediationsPage)
