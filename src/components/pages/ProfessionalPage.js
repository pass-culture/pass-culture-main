import React from 'react'

import OfferersGrid from '../pro/OfferersGrid'
import withLogin from '../hocs/withLogin'

const ProfessionalPage = () => {
  return (
    <main className="page professional-page p2 center">
      <div className="h2 mt2">Mes offres</div>
      <OfferersGrid />
    </main>
  )
}

export default withLogin({ isRequired: true })(ProfessionalPage)
