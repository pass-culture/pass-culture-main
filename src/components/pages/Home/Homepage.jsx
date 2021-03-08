import React from 'react'

import PageTitle from 'components/layout/PageTitle/PageTitle'

import Breadcrumb, { STEP_ID_OFFERERS } from './HomepageBreadcrumb'
import OfferersContainer from './Offerers/OfferersContainer'
import ProfileAndSupportContainer from './ProfileAndSupport/ProfileAndSupportContainer'

const Homepage = () => (
  <div className="homepage">
    <PageTitle title="Espace acteurs culturels" />
    <h1>
      {'Bienvenue dans l’espace acteurs culturels'}
    </h1>

    <Breadcrumb activeStep={STEP_ID_OFFERERS} />

    <section className="h-section">
      <OfferersContainer />
    </section>

    <section className="h-section">
      <ProfileAndSupportContainer />
    </section>
  </div>
)

export default Homepage
