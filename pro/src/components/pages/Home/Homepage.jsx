import React, { useRef } from 'react'

import PageTitle from 'components/layout/PageTitle/PageTitle'

import HomepageBreadcrumb, { STEP_ID_OFFERERS } from './HomepageBreadcrumb'
import Offerers from './Offerers/Offerers'
import { ProfileAndSupport } from './ProfileAndSupport'

const Homepage = () => {
  const profileRef = useRef(null)

  return (
    <div className="homepage">
      <PageTitle title="Espace acteurs culturels" />
      <h1>Bienvenue dans l’espace acteurs culturels</h1>

      <HomepageBreadcrumb
        activeStep={STEP_ID_OFFERERS}
        profileRef={profileRef}
      />

      <section className="h-section">
        <Offerers />
      </section>

      <section className="h-section" ref={profileRef}>
        <ProfileAndSupport />
      </section>
    </div>
  )
}

export default Homepage
