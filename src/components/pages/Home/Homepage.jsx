import React from 'react'

import PageTitle from 'components/layout/PageTitle/PageTitle'

import Breadcrumb, { STEP_ID_OFFERERS } from './HomepageBreadcrumb'
import Offerers from './Offerers'
import ProfileAndSupportContainer from './ProfileAndSupport/ProfileAndSupportContainer'
import Usages from './Usages'

const Homepage = () => {
  const activeStep = STEP_ID_OFFERERS

  return (
    <div className="homepage">
      <PageTitle title="Espace acteurs culturels" />
      <h1>
        {'Bienvenue dans l’espace acteurs culturels'}
      </h1>

      <Breadcrumb activeStep={activeStep} />

      <section className="h-section">
        <Offerers />
      </section>

      <section className="h-section">
        <ProfileAndSupportContainer />
      </section>

      <section className="h-section">
        <Usages />
      </section>
    </div>
  )
}

export default Homepage
