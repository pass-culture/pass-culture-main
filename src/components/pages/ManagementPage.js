import React from 'react'

import OfferersList from '../OfferersList'
import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'


const ManagementPage = () => {
  return (
    <PageWrapper menuButton name="professional">
      <OfferersList />
    </PageWrapper>
  )
}

export default withLogin({ isRequired: true })(ManagementPage)
