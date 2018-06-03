import React from 'react'
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
