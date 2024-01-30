import { useEffect, useMemo, useRef, useState } from 'react'
import { RouteObject, useLoaderData, useSearchParams } from 'react-router-dom'

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
import { SelectOption } from 'custom_types/form'
import useRemoteConfig from 'hooks/useRemoteConfig'
import { HTTP_STATUS } from 'repository/pcapi/pcapiClient'
import { localStorageAvailable } from 'utils/localStorageAvailable'
import { sortByLabel } from 'utils/strings'

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

export const SAVED_OFFERER_ID_KEY = 'homepageSelectedOffererId'
const getSavedOffererId = (offererOptions: SelectOption[]): string | null => {
  const isLocalStorageAvailable = localStorageAvailable()
  if (!isLocalStorageAvailable) {
    return null
  }

  const savedOffererId = localStorage.getItem(SAVED_OFFERER_ID_KEY)
  if (
    !savedOffererId ||
    !offererOptions.map((option) => option.value).includes(savedOffererId)
  ) {
    return null
  }

  return savedOffererId
}

export const Homepage = (): JSX.Element => {
  const profileRef = useRef<HTMLElement>(null)
  const offerersRef = useRef<HTMLElement>(null)
  const [searchParams] = useSearchParams()
  const { offererNames } = useLoaderData() as HomepageLoaderData

  const [selectedOfferer, setSelectedOfferer] =
    useState<GetOffererResponseModel | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isUserOffererValidated, setIsUserOffererValidated] = useState(false)
  const { remoteConfigData } = useRemoteConfig()

  const hasNoVenueVisible = useMemo(() => {
    const physicalVenues = getPhysicalVenuesFromOfferer(selectedOfferer)
    const virtualVenue = getVirtualVenueFromOfferer(selectedOfferer)

    return physicalVenues?.length === 0 && !virtualVenue
  }, [selectedOfferer])

  const offererOptions = sortByLabel(
    offererNames.map((item) => ({
      value: item['id'].toString(),
      label: item['name'],
    }))
  )
  const selectedOffererId =
    searchParams.get('structure') ??
    getSavedOffererId(offererOptions) ??
    offererOptions[0]?.value ??
    ''

  useEffect(() => {
    async function loadOfferer(offererId: string) {
      setIsLoading(true)

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
            hasActiveOffer: false,
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
        <OffererBanners
          isUserOffererValidated={isUserOffererValidated}
          offerer={selectedOfferer}
        />
      )}

      {selectedOfferer?.isValidated && selectedOfferer?.isActive && (
        <section className={styles['section']}>
          <StatisticsDashboard offerer={selectedOfferer} />
        </section>
      )}

      <section className={styles['section']} ref={offerersRef}>
        <Offerers
          selectedOfferer={selectedOfferer}
          isLoading={isLoading}
          offererOptions={offererOptions}
          isUserOffererValidated={isUserOffererValidated}
          setSelectedOfferer={setSelectedOfferer}
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
