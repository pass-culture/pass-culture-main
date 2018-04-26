import React from 'react'

import OfferersGrid from '../pro/OfferersGrid'
import withLogin from '../hocs/withLogin'
import PageWrapper from '../layout/PageWrapper'

const ProfessionalPage = () => {
  return (
    <PageWrapper name="professional">
      <div className="h2 mt2">Mes offres</div>
      <OfferersGrid />
    </PageWrapper>
  )
}

export default withLogin({ isRequired: true })(ProfessionalPage)
