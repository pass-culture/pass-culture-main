import React, { useEffect, useRef, useState } from 'react'

import useCurrentUser from 'components/hooks/useCurrentUser'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import { BannerRGS } from 'new_components/Banner'
import { BannerHeritageDay } from 'new_components/BannerHeritageDay'
import { BannerOneYear } from 'new_components/BannerOneYear'
import { Newsletter } from 'new_components/Newsletter'
import { setHasSeenRGSBanner } from 'repository/pcapi/pcapi'

import useActiveFeature from '../../hooks/useActiveFeature'

import HomepageBreadcrumb, { STEP_ID_OFFERERS } from './HomepageBreadcrumb'
import Offerers from './Offerers/Offerers'
import { ProfileAndSupport } from './ProfileAndSupport'

const Homepage = (): JSX.Element => {
  const profileRef = useRef(null)
  const {
    currentUser: { hasSeenProRgs },
  } = useCurrentUser()
  const [hasClosedRGSBanner, setHasClosedRGSBanner] = useState<boolean>(
    Boolean(hasSeenProRgs)
  )
  const handleCloseRGSBanner = () => {
    setHasSeenRGSBanner().finally(() => {
      setHasClosedRGSBanner(true)
    })
  }

  const IsBannerOneYearActive = useActiveFeature('ENABLE_BANNER_ONE_YEAR')

  const [venues, setVenues] = useState([])
  const [showBanner, setShowBanner] = useState(false)

  useEffect(() => {
    if (
      venues.some(({ venueTypeCode }) => venueTypeCode === 'PATRIMONY_TOURISM')
    ) {
      setShowBanner(true)
    }
  }, [venues])

  return (
    <div className="homepage">
      <PageTitle title="Espace acteurs culturels" />
      <h1>Bienvenue dans l’espace acteurs culturels</h1>
      {IsBannerOneYearActive && <BannerOneYear />}
      {showBanner && <BannerHeritageDay />}
      {!hasClosedRGSBanner && (
        <BannerRGS closable onClose={handleCloseRGSBanner} />
      )}
      <HomepageBreadcrumb
        activeStep={STEP_ID_OFFERERS}
        profileRef={profileRef}
      />

      <section className="h-section">
        <Offerers setVenues={setVenues} />
      </section>

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
