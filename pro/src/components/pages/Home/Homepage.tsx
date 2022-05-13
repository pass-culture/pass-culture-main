import HomepageBreadcrumb, { STEP_ID_OFFERERS } from './HomepageBreadcrumb'
import React, { useRef, useState } from 'react'

import { BannerRGS } from 'new_components/Banner'
import Offerers from './Offerers/Offerers'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import { ProfileAndSupport } from './ProfileAndSupport'
import { setHasSeenRGSBanner } from 'repository/pcapi/pcapi'
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

  return (
    <div className="homepage">
      <PageTitle title="Espace acteurs culturels" />
      <h1>Bienvenue dans l’espace acteurs culturels</h1>
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
      </section>
    </div>
  )
}

export default Homepage
