import React, { useEffect, useRef, useState } from 'react'

import { api } from 'apiClient/api'
import {
  GetOffererResponseModel,
  GetOfferersNamesResponseModel,
} from 'apiClient/v1'
import AddBankAccountCallout from 'components/Callout/AddBankAccountCallout'
import LinkVenueCallout from 'components/Callout/LinkVenueCallout'
import PendingBankAccountCallout from 'components/Callout/PendingBankAccountCallout'
import { Newsletter } from 'components/Newsletter'
import TutorialDialog from 'components/TutorialDialog'
import { hasStatusCode } from 'core/OfferEducational'
import useActiveFeature from 'hooks/useActiveFeature'
import useRemoteConfig from 'hooks/useRemoteConfig'
import { INITIAL_OFFERER_VENUES } from 'pages/Home/OffererVenues'
import { HTTP_STATUS } from 'repository/pcapi/pcapiClient'

import styles from './Homepage.module.scss'
import HomepageBreadcrumb, { STEP_ID_OFFERERS } from './HomepageBreadcrumb'
import Offerers from './Offerers/Offerers'
import { OffererStats } from './OffererStats'
import { ProfileAndSupport } from './ProfileAndSupport'
import { StatisticsDashboard } from './StatisticsDashboard/StatisticsDashboard'
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
  const isStatisticsDashboardEnabled = useActiveFeature('WIP_HOME_STATS')

  useEffect(() => {
    async function loadOfferer(offererId: string) {
      try {
        const receivedOfferer = await api.getOfferer(Number(offererId))
        const offererPhysicalVenues =
          receivedOfferer.managedVenues?.filter((venue) => !venue.isVirtual) ??
          []
        const virtualVenue =
          receivedOfferer.managedVenues?.find((venue) => venue.isVirtual) ??
          null
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
            hasAvailablePricingPoints: false,
            hasDigitalVenueAtLeastOneOffer: false,
            hasValidBankAccount: true,
            hasPendingBankAccount: false,
            venuesWithNonFreeOffersWithoutBankAccounts: [],
            isActive: false,
            isValidated: false,
            managedVenues: [],
            name: '',
            id: Number(offererId) ?? 0,
            postalCode: '',
            dsToken: '',
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

  useEffect(function fetchData() {
    api.listOfferersNames().then(async (offererNames) => {
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

        <div className={styles['reimbursements-banners']}>
          <AddBankAccountCallout offerer={selectedOfferer} />
          <LinkVenueCallout offerer={selectedOfferer} />
          <PendingBankAccountCallout offerer={selectedOfferer} />
        </div>
        <HomepageBreadcrumb
          activeStep={STEP_ID_OFFERERS}
          isOffererStatsActive={isOffererStatsActive}
          profileRef={profileRef}
          statsRef={statsRef}
        />

        {isStatisticsDashboardEnabled && (
          <StatisticsDashboard offererId={selectedOffererId} />
        )}

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

        {isUserOffererValidated && hasNoVenueVisible && (
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
