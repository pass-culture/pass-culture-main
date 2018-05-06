import React from 'react'

import OfferersGrid from '../OfferersGrid'
import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'


const ManagementPage = () => {
  return (
    <PageWrapper menuButton name="professional">
      <OfferersGrid />
    </PageWrapper>
  )
}

export default withLogin({ isRequired: true })(ManagementPage)
