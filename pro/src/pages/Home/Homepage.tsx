import React, { useEffect, useRef, useState } from 'react'

import { Newsletter } from 'components/Newsletter'
import PageTitle from 'components/PageTitle/PageTitle'
import useActiveFeature from 'hooks/useActiveFeature'

import { api } from '../../apiClient/api'
import {
  GetOfferersNamesResponseModel,
  GetOffererVenueResponseModel,
} from '../../apiClient/v1'
import useNewOfferCreationJourney from '../../hooks/useNewOfferCreationJourney'

import HomepageBreadcrumb, { STEP_ID_OFFERERS } from './HomepageBreadcrumb'
import Offerers from './Offerers/Offerers'
import { OffererStats } from './OffererStats'
import { ProfileAndSupport } from './ProfileAndSupport'
import { VenueOfferSteps } from './VenueOfferSteps'

const Homepage = (): JSX.Element => {
  const profileRef = useRef(null)
  const statsRef = useRef(null)

  const [receivedOffererNames, setReceivedOffererNames] =
    useState<GetOfferersNamesResponseModel | null>(null)
  const [venues, setVenues] = useState<GetOffererVenueResponseModel[]>([])
  const [offererId, setOffererId] = useState('')

  const isOffererStatsActive = useActiveFeature('ENABLE_OFFERER_STATS')
  const withNewOfferCreationJourney = useNewOfferCreationJourney()

  useEffect(function fetchData() {
    api.listOfferersNames().then(async offererNames => {
      setReceivedOffererNames(offererNames)
      if (offererNames.offerersNames.length === 1) {
        const offerer = offererNames.offerersNames[0].id
        setOffererId(offerer)
        const receivedOfferer = await api.getOfferer(offerer)
        setVenues(
          /* istanbul ignore next: DEBT, TO FIX */
          receivedOfferer.managedVenues
            ? receivedOfferer.managedVenues.filter(venue => !venue.isVirtual)
            : []
        )
      }
    })
  }, [])

  return (
    <div className="homepage">
      <PageTitle title="Espace acteurs culturels" />
      <h1>Bienvenue dans l’espace acteurs culturels</h1>
      <HomepageBreadcrumb
        activeStep={STEP_ID_OFFERERS}
        isOffererStatsActive={isOffererStatsActive}
        profileRef={profileRef}
        statsRef={statsRef}
      />
      <section className="h-section">
        <Offerers receivedOffererNames={receivedOffererNames} />
      </section>
      {withNewOfferCreationJourney &&
        receivedOffererNames?.offerersNames.length === 1 &&
        venues.length === 0 && (
          <section className="h-section">
            <VenueOfferSteps
              hasVenue={venues.length > 0}
              offererId={offererId}
            />
          </section>
        )}
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
