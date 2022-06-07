import HomepageBreadcrumb, { STEP_ID_OFFERERS } from './HomepageBreadcrumb'
import React, { useRef, useState } from 'react'

import { BannerOneYear } from 'new_components/BannerOneYear'
import { BannerRGS } from 'new_components/Banner'
import { Newsletter } from 'new_components/Newsletter'
import Offerers from './Offerers/Offerers'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import { ProfileAndSupport } from './ProfileAndSupport'
import { setHasSeenRGSBanner } from 'repository/pcapi/pcapi'
import useActiveFeature from '../../hooks/useActiveFeature'
import useCurrentUser from 'components/hooks/useCurrentUser'

const Homepage = (): JSX.Element => {
  const profileRef = useRef(null)
  const {
    currentUser: { hasSeenProRgs },
  } = useCurrentUser()
  const [hasClosedRGSBanner, setHasClosedRGSBanner] =
    useState<boolean>(hasSeenProRgs)
  const handleCloseRGSBanner = () => {
    setHasSeenRGSBanner().finally(() => {
      setHasClosedRGSBanner(true)
    })
  }

  const IsBannerOneYearActive = useActiveFeature('ENABLE_BANNER_ONE_YEAR')

  return (
    <div className="homepage">
      <PageTitle title="Espace acteurs culturels" />
      <h1>Bienvenue dans l’espace acteurs culturels</h1>
      {IsBannerOneYearActive && <BannerOneYear/>}
      {!hasClosedRGSBanner && (
        <BannerRGS closable onClose={handleCloseRGSBanner} />
      )}
      <HomepageBreadcrumb
        activeStep={STEP_ID_OFFERERS}
        profileRef={profileRef}
      />

      <section className="h-section">
        <Offerers />
      </section>

      <section className="h-section" ref={profileRef}>
        <ProfileAndSupport />
        <div className="newsletter">
          <Newsletter/>
        </div>
      </section>
    </div>
  )
}

export default Homepage
