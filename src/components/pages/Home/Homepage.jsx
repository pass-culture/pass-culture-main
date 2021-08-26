/*
* @debt directory "Gaël: this file should be migrated within the new directory structure"
*/

import PropTypes from 'prop-types'
import React, { useRef } from 'react'

import PageTitle from 'components/layout/PageTitle/PageTitle'

import HomepageBreadcrumb, { STEP_ID_OFFERERS } from './HomepageBreadcrumb'
import Offerers from './Offerers/Offerers'
import OfferersLegacy from './Offerers/OfferersLegacy'
import ProfileAndSupportContainer from './ProfileAndSupport/ProfileAndSupportContainer'

const Homepage = props => {
  const { isPerfVenueStatsEnabled } = props
  const profileRef = useRef(null)

  return (
    <div className="homepage">
      <PageTitle title="Espace acteurs culturels" />
      <h1>
        Bienvenue dans l’espace acteurs culturels
      </h1>

      <HomepageBreadcrumb
        activeStep={STEP_ID_OFFERERS}
        profileRef={profileRef}
      />

      <section className="h-section">
        {isPerfVenueStatsEnabled ? <Offerers /> : <OfferersLegacy />}
      </section>

      <section
        className="h-section"
        ref={profileRef}
      >
        <ProfileAndSupportContainer />
      </section>
    </div>
  )
}

Homepage.defaultProps = {
  isPerfVenueStatsEnabled: false,
}

Homepage.propTypes = {
  isPerfVenueStatsEnabled: PropTypes.bool,
}

export default Homepage
