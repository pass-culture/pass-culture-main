import React, { useEffect, useRef, useState } from 'react'

import { api } from 'apiClient/api'
import {
  GetOffererResponseModel,
  GetOfferersNamesResponseModel,
} from 'apiClient/v1'
import { Newsletter } from 'components/Newsletter'
import TutorialDialog from 'components/TutorialDialog'
import { hasStatusCode } from 'core/OfferEducational'
import useActiveFeature from 'hooks/useActiveFeature'
import useRemoteConfig from 'hooks/useRemoteConfig'
import { INITIAL_OFFERER_VENUES } from 'pages/Home/OffererVenues'
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
  const [selectedOffererId, setSelectedOffererId] = useState<string>('')
  const [selectedOfferer, setSelectedOfferer] =
    useState<GetOffererResponseModel | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [hasNoVenueVisible, setHasNoVenueVisible] = useState(false)
  const [isUserOffererValidated, setIsUserOffererValidated] = useState(false)
  const [venues, setVenues] = useState(INITIAL_OFFERER_VENUES)
  const { remoteConfigData } = useRemoteConfig()

  useEffect(() => {
    async function loadOfferer(offererId: string) {
      try {
        const receivedOfferer = await api.getOfferer(Number(offererId))
        const offererPhysicalVenues =
          receivedOfferer.managedVenues?.filter(venue => !venue.isVirtual) ?? []
        const virtualVenue =
          receivedOfferer.managedVenues?.find(venue => venue.isVirtual) ?? null
        setHasNoVenueVisible(
          offererPhysicalVenues?.length === 0 && !virtualVenue?.hasCreatedOffer
        )
        setVenues({
          physicalVenues: offererPhysicalVenues,
          virtualVenue: virtualVenue,
        })
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
            id: offererId,
            isActive: false,
            isValidated: false,
            managedVenues: [],
            name: '',
            nonHumanizedId: Number(offererId) ?? 0,
            postalCode: '',
          })
          setVenues(INITIAL_OFFERER_VENUES)
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
    })
  }, [])

  useEffect(() => {
    if (remoteConfigData != null) {
      api.postProFlags({
        firebase: remoteConfigData,
      })
    }
  }, [remoteConfigData])

  return (
    <>
      <div className="homepage">
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
            venues={venues}
          />
        </section>
        {isUserOffererValidated &&
          withNewOfferCreationJourney &&
          hasNoVenueVisible && (
            <section className="step-section">
              <VenueOfferSteps
                hasVenue={!hasNoVenueVisible}
                offererId={Number(selectedOffererId)}
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
      <TutorialDialog />
    </>
  )
}

export default Homepage
