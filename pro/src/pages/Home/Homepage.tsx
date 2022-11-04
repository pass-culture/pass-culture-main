import React, { useRef } from 'react'

import JobHighlightsBanner from 'components/JobHighlightsBanner'
import { Newsletter } from 'components/Newsletter'
import PageTitle from 'components/PageTitle/PageTitle'
import useActiveFeature from 'hooks/useActiveFeature'

import HomepageBreadcrumb, { STEP_ID_OFFERERS } from './HomepageBreadcrumb'
import Offerers from './Offerers/Offerers'
import { OffererStats } from './OffererStats'
import { ProfileAndSupport } from './ProfileAndSupport'

const Homepage = (): JSX.Element => {
  const profileRef = useRef(null)
  const statsRef = useRef(null)
  const isOffererStatsActive = useActiveFeature('ENABLE_OFFERER_STATS')
  const isJobHighlightBannerEnabled = useActiveFeature(
    'TEMP_ENABLE_JOB_HIGHLIGHTS_BANNER'
  )

  return (
    <div className="homepage">
      <PageTitle title="Espace acteurs culturels" />
      <h1>Bienvenue dans l’espace acteurs culturels</h1>
      {isJobHighlightBannerEnabled && <JobHighlightsBanner />}
      <HomepageBreadcrumb
        activeStep={STEP_ID_OFFERERS}
        isOffererStatsActive={isOffererStatsActive}
        profileRef={profileRef}
        statsRef={statsRef}
      />
      <section className="h-section">
        <Offerers />
      </section>
      {isOffererStatsActive && (
        <section className="h-section" ref={statsRef}>
          <OffererStats />
        </section>
      )}
      <section className="h-section" ref={profileRef}>
        <ProfileAndSupport />
        <div className="newsletter">
          <Newsletter />
        </div>
      </section>
    </div>
  )
}

export default Homepage
