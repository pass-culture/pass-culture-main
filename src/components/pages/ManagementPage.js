import React from 'react'

import OfferersGrid from '../OfferersGrid'
import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'

const ManagementPage = () => {
  return (
    <PageWrapper name="professional">
      <div className="h2 mt2">Mes offres</div>
      <OfferersGrid />
    </PageWrapper>
  )
}

export default withLogin({ isRequired: true })(ManagementPage)
