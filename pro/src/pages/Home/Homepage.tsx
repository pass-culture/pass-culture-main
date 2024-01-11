import React, { useEffect, useMemo, useRef, useState } from 'react'
import { RouteObject } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  GetOffererNameResponseModel,
  GetOffererResponseModel,
  VenueTypeResponseModel,
} from 'apiClient/v1'
import { AppLayout } from 'app/AppLayout'
import AddBankAccountCallout from 'components/Callout/AddBankAccountCallout'
import LinkVenueCallout from 'components/Callout/LinkVenueCallout'
import PendingBankAccountCallout from 'components/Callout/PendingBankAccountCallout'
import { Newsletter } from 'components/Newsletter'
import TutorialDialog from 'components/TutorialDialog'
import { hasStatusCode } from 'core/OfferEducational'
import useRemoteConfig from 'hooks/useRemoteConfig'
import { HTTP_STATUS } from 'repository/pcapi/pcapiClient'

import styles from './Homepage.module.scss'
import { OffererBanners } from './Offerers/OffererBanners'
import Offerers from './Offerers/Offerers'
import { ProfileAndSupport } from './ProfileAndSupport/ProfileAndSupport'
import { StatisticsDashboard } from './StatisticsDashboard/StatisticsDashboard'
import { VenueOfferSteps } from './VenueOfferSteps/VenueOfferSteps'
import {
  getPhysicalVenuesFromOfferer,
  getVirtualVenueFromOfferer,
} from './venueUtils'

export const Homepage = (): JSX.Element => {
  const profileRef = useRef<HTMLElement>(null)
  const offerersRef = useRef<HTMLElement>(null)

  const [selectedOffererId, setSelectedOffererId] = useState<string>('')
  const [selectedOfferer, setSelectedOfferer] =
    useState<GetOffererResponseModel | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isUserOffererValidated, setIsUserOffererValidated] = useState(false)
  const { remoteConfigData } = useRemoteConfig()

  const hasNoVenueVisible = useMemo(() => {
    const physicalVenues = getPhysicalVenuesFromOfferer(selectedOfferer)
    const virtualVenue = getVirtualVenueFromOfferer(selectedOfferer)

    return physicalVenues?.length === 0 && !virtualVenue
  }, [selectedOfferer])

  useEffect(() => {
    async function loadOfferer(offererId: string) {
      try {
        const offerer = await api.getOfferer(Number(offererId))
        setSelectedOfferer(offerer)
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
            hasNonFreeOffer: true,
            venuesWithNonFreeOffersWithoutBankAccounts: [],
            isActive: false,
            isValidated: false,
            managedVenues: [],
            name: '',
            id: Number(offererId) ?? 0,
            postalCode: '',
          })
          setIsUserOffererValidated(false)
        }
      }
      setIsLoading(false)
    }

    if (selectedOffererId) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      loadOfferer(selectedOffererId)
    }
  }, [selectedOffererId])

  useEffect(() => {
    async function logProFlags() {
      if (remoteConfigData !== null) {
        await api.postProFlags({
          firebase: remoteConfigData,
        })
      }
    }
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    logProFlags()
  }, [remoteConfigData?.REMOTE_CONFIG_LOADED])

  return (
    <AppLayout>
      <h1>Bienvenue dans l’espace acteurs culturels</h1>

      <div className={styles['reimbursements-banners']}>
        <AddBankAccountCallout offerer={selectedOfferer} />
        <LinkVenueCallout offerer={selectedOfferer} />
        <PendingBankAccountCallout offerer={selectedOfferer} />
      </div>

      {selectedOfferer !== null && (
        <>
          <OffererBanners
            isUserOffererValidated={isUserOffererValidated}
            offerer={selectedOfferer}
          />

          <section className={styles['section']}>
            <StatisticsDashboard offerer={selectedOfferer} />
          </section>
        </>
      )}

      <section className={styles['section']} ref={offerersRef}>
        <Offerers
          selectedOfferer={selectedOfferer}
          isLoading={isLoading}
          isUserOffererValidated={isUserOffererValidated}
          onSelectedOffererChange={setSelectedOffererId}
          cancelLoading={() => setIsLoading(false)}
        />
      </section>

      {isUserOffererValidated &&
        hasNoVenueVisible &&
        selectedOfferer !== null && (
          <section className={styles['step-section']}>
            <VenueOfferSteps
              hasVenue={!hasNoVenueVisible}
              offerer={selectedOfferer}
            />
          </section>
        )}

      <section className={styles['section']} ref={profileRef}>
        <ProfileAndSupport />

        <div className={styles['newsletter']}>
          <Newsletter />
        </div>
      </section>

      <TutorialDialog />
    </AppLayout>
  )
}

// Below exports are used by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Homepage

export type HomepageLoaderData = {
  venueTypes: VenueTypeResponseModel[]
  offererNames: GetOffererNameResponseModel[]
}

// ts-unused-exports:disable-next-line
export const loader: RouteObject['loader'] =
  async (): Promise<HomepageLoaderData> => {
    const venueTypes = await api.getVenueTypes()
    const offererNamesResponse = await api.listOfferersNames()

    return {
      venueTypes,
      offererNames: offererNamesResponse.offerersNames,
    }
  }

// ts-unused-exports:disable-next-line
export const shouldRevalidate: RouteObject['shouldRevalidate'] = () => {
  return false
}
