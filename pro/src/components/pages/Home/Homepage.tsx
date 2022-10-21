import { getValue } from '@firebase/remote-config'
import React, { useEffect, useRef, useState } from 'react'

import { api } from 'apiClient/api'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import useActiveFeature from 'hooks/useActiveFeature'
import useCurrentUser from 'hooks/useCurrentUser'
import useRemoteConfig from 'hooks/useRemoteConfig'
import { BannerRGS } from 'new_components/Banner'
import { Newsletter } from 'new_components/Newsletter'

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
  const [canSeeStats, setCanSeeStats] = useState<boolean>(false)
  const isOffererStatsActive = useActiveFeature('ENABLE_OFFERER_STATS')
  const handleCloseRGSBanner = () => {
    api.patchProUserRgsSeen().finally(() => {
      setHasClosedRGSBanner(true)
    })
  }
  const { remoteConfig } = useRemoteConfig()
  useEffect(() => {
    if (isOffererStatsActive) {
      api.listOfferersNames().then(receivedOffererNames => {
        let biggest500: string[] = []
        if (remoteConfig) {
          biggest500 = getValue(remoteConfig, 'only500BiggerActors')
            .asString()
            .split(',')
        }
        setCanSeeStats(
          receivedOffererNames.offerersNames.some(v =>
            biggest500.includes(v.id)
          )
        )
      })
    }
  }, [remoteConfig])

  return (
    <div className="homepage">
      <PageTitle title="Espace acteurs culturels" />
      <h1>Bienvenue dans l’espace acteurs culturels</h1>
      {!hasClosedRGSBanner && (
        <BannerRGS closable onClose={handleCloseRGSBanner} />
      )}
      <HomepageBreadcrumb
        activeStep={STEP_ID_OFFERERS}
        isOffererStatsActive={isOffererStatsActive && canSeeStats}
        profileRef={profileRef}
        statsRef={statsRef}
      />
      <section className="h-section">
        <Offerers />
      </section>
      {isOffererStatsActive && canSeeStats && (
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
