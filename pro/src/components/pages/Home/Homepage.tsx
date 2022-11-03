import React, { useRef, useState } from 'react'

import { api } from 'apiClient/api'
import useActiveFeature from 'hooks/useActiveFeature'
import useCurrentUser from 'hooks/useCurrentUser'
import { BannerRGS } from 'new_components/Banner'
import JobHighlightsBanner from 'new_components/JobHighlightsBanner'
import { Newsletter } from 'new_components/Newsletter'
import PageTitle from 'new_components/PageTitle/PageTitle'

import HomepageBreadcrumb, { STEP_ID_OFFERERS } from './HomepageBreadcrumb'
import Offerers from './Offerers/Offerers'
import { OffererStats } from './OffererStats'
import { ProfileAndSupport } from './ProfileAndSupport'

const Homepage = (): JSX.Element => {
  const profileRef = useRef(null)
  const statsRef = useRef(null)
  const {
    currentUser: { hasSeenProRgs },
  } = useCurrentUser()
  const [hasClosedRGSBanner, setHasClosedRGSBanner] = useState<boolean>(
    Boolean(hasSeenProRgs)
  )
  const isOffererStatsActive = useActiveFeature('ENABLE_OFFERER_STATS')
  const handleCloseRGSBanner = () => {
    api.patchProUserRgsSeen().finally(() => {
      setHasClosedRGSBanner(true)
    })
  }

  const isJobHighlightBannerEnabled = useActiveFeature(
    'TEMP_ENABLE_JOB_HIGHLIGHTS_BANNER'
  )

  return (
    <div className="homepage">
      <PageTitle title="Espace acteurs culturels" />
      <h1>Bienvenue dans l’espace acteurs culturels</h1>
      {isJobHighlightBannerEnabled && <JobHighlightsBanner />}
      {!hasClosedRGSBanner && (
        <BannerRGS closable onClose={handleCloseRGSBanner} />
      )}
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
