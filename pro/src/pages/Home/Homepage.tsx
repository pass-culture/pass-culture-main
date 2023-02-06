import React, { useEffect, useRef, useState } from 'react'

import { api } from 'apiClient/api'
import {
  GetOffererResponseModel,
  GetOfferersNamesResponseModel,
  GetOffererVenueResponseModel,
} from 'apiClient/v1'
import { Newsletter } from 'components/Newsletter'
import PageTitle from 'components/PageTitle/PageTitle'
import { hasStatusCode } from 'core/OfferEducational'
import useActiveFeature from 'hooks/useActiveFeature'
import { HTTP_STATUS } from 'repository/pcapi/pcapiClient'

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
  const [selectedOffererId, setSelectedOffererId] = useState<string | null>(
    null
  )
  const [selectedOfferer, setSelectedOfferer] =
    useState<GetOffererResponseModel | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isUserOffererValidated, setIsUserOffererValidated] = useState(false)

  useEffect(() => {
    async function loadOfferer(offererId: string) {
      try {
        const receivedOfferer = await api.getOfferer(offererId)
        setSelectedOfferer(receivedOfferer)
        setIsUserOffererValidated(true)
      } catch (error) {
        /* istanbul ignore next: DEBT, TO FIX */
        if (hasStatusCode(error) && error.status === HTTP_STATUS.FORBIDDEN) {
          setSelectedOfferer({
            apiKey: {
              maxAllowed: 0,
              prefixes: [],
            },
            city: '',
            dateCreated: '',
            fieldsUpdated: [],
            hasAvailablePricingPoints: false,
            hasDigitalVenueAtLeastOneOffer: false,
            hasMissingBankInformation: true,
            id: offererId,
            isActive: false,
            isValidated: false,
            managedVenues: [],
            name: '',
            nonHumanizedId: 0,
            postalCode: '',
          })
          setIsUserOffererValidated(false)
        }
      }
      setIsLoading(false)
    }
    selectedOffererId && loadOfferer(selectedOffererId)
  }, [selectedOffererId])

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
        <Offerers
          selectedOfferer={selectedOfferer}
          isLoading={isLoading}
          isUserOffererValidated={isUserOffererValidated}
          receivedOffererNames={receivedOffererNames}
          onSelectedOffererChange={setSelectedOffererId}
          cancelLoading={() => setIsLoading(false)}
        />
      </section>
      {isUserOffererValidated &&
        withNewOfferCreationJourney &&
        receivedOffererNames?.offerersNames.length === 1 &&
        venues.length === 0 && (
          <section className="step-section">
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
