import React, { useEffect, useMemo, useRef, useState } from 'react'
import { useDispatch } from 'react-redux'
import {
  RouteObject,
  useLoaderData,
  useNavigate,
  useSearchParams,
} from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  GetOffererNameResponseModel,
  GetOffererResponseModel,
  VenueTypeResponseModel,
} from 'apiClient/v1'
import { AppLayout } from 'app/AppLayout'
import AddBankAccountCallout from 'components/Callout/AddBankAccountCallout'
import BankAccountHasPendingCorrectionCallout from 'components/Callout/BankAccountHasPendingCorrectionCallout'
import LinkVenueCallout from 'components/Callout/LinkVenueCallout'
import DialogBox from 'components/DialogBox'
import { Newsletter } from 'components/Newsletter'
import TutorialDialog from 'components/TutorialDialog'
import { hasStatusCode } from 'core/OfferEducational'
import { SAVED_OFFERER_ID_KEY } from 'core/shared'
import { SelectOption } from 'custom_types/form'
import useActiveFeature from 'hooks/useActiveFeature'
import useCurrentUser from 'hooks/useCurrentUser'
import useIsNewInterfaceActive from 'hooks/useIsNewInterfaceActive'
import useNotification from 'hooks/useNotification'
import useRemoteConfig from 'hooks/useRemoteConfig'
import strokeCloseIcon from 'icons/stroke-close.svg'
import { HTTP_STATUS } from 'repository/pcapi/pcapiClient'
import { updateSelectedOffererId } from 'store/user/reducer'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { formatBrowserTimezonedDateAsUTC, isDateValid } from 'utils/date'
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

const getSavedOffererId = (offererOptions: SelectOption[]): string | null => {
  const isLocalStorageAvailable = localStorageAvailable()
  if (!isLocalStorageAvailable) {
    return null
  }

  const savedOffererId = localStorage.getItem(SAVED_OFFERER_ID_KEY)
  if (
    savedOffererId &&
    !offererOptions.map((option) => option.value).includes(savedOffererId)
  ) {
    return null
  }

  return savedOffererId
}

export const Homepage = (): JSX.Element => {
  const HAS_CLOSED_BETA_TEST_BANNER = 'HAS_CLOSED_BETA_TEST_BANNER'
  const NEW_NAV_ENABLED = 'NEW_NAV_ENABLED'

  const profileRef = useRef<HTMLElement>(null)
  const offerersRef = useRef<HTMLElement>(null)
  const [searchParams, setSearchParams] = useSearchParams()
  const { offererNames } = useLoaderData() as HomepageLoaderData
  const navigate = useNavigate()
  const isNewNavActive = useActiveFeature('WIP_ENABLE_PRO_SIDE_NAV')
  const hasNewSideBarNavigation = useIsNewInterfaceActive()
  const { currentUser } = useCurrentUser()
  const notify = useNotification()

  const userClosedBetaTestBanner = localStorageAvailable()
    ? !localStorage.getItem(HAS_CLOSED_BETA_TEST_BANNER)
    : true
  const isEligibleToNewNav =
    isDateValid(currentUser.navState?.eligibilityDate) &&
    new Date(currentUser.navState.eligibilityDate) <=
      new Date(formatBrowserTimezonedDateAsUTC(new Date()))

  const [selectedOfferer, setSelectedOfferer] =
    useState<GetOffererResponseModel | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isUserOffererValidated, setIsUserOffererValidated] = useState(false)
  const [seesNewNavAvailableBanner, setSeesNewNavAvailableBanner] = useState(
    userClosedBetaTestBanner &&
      isNewNavActive &&
      !hasNewSideBarNavigation &&
      isEligibleToNewNav
  )

  const [isNewNavEnabled, setIsNewNavEnabled] = useState(false)
  const { remoteConfigData } = useRemoteConfig()
  const dispatch = useDispatch()

  const hasNoVenueVisible = useMemo(() => {
    const physicalVenues = getPhysicalVenuesFromOfferer(selectedOfferer)
    const virtualVenue = getVirtualVenueFromOfferer(selectedOfferer)

    return physicalVenues.length === 0 && !virtualVenue
  }, [selectedOfferer])

  async function showNewNav() {
    try {
      await api.postNewProNav()
      hideBanner()
      navigate({ search: `${location.search}&${NEW_NAV_ENABLED}=true` })

      // We need to reload so the new interface is loaded.
      window.location.reload()
    } catch (error) {
      notify.error("Impossible de réaliser l'action. Réessayez plus tard")
    }
  }

  function hideBanner() {
    localStorageAvailable() &&
      localStorage.setItem(HAS_CLOSED_BETA_TEST_BANNER, 'true')
    setSeesNewNavAvailableBanner(false)
  }

  // TODO: remove when removing WIP_ENABLE_PRO_SIDE_NAV
  useEffect(() => {
    if (searchParams.get(NEW_NAV_ENABLED)) {
      searchParams.delete(NEW_NAV_ENABLED)
      setSearchParams(searchParams)
      setIsNewNavEnabled(true)
    }
  }, [searchParams.get(NEW_NAV_ENABLED)])

  const offererOptions = sortByLabel(
    offererNames.map((item) => ({
      value: item['id'].toString(),
      label: item['name'],
    }))
  )

  const selectedOffererId =
    // TODO remove this when noUncheckedIndexedAccess is enabled in TS config
    // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition
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
        localStorage.setItem(SAVED_OFFERER_ID_KEY, offererId)
        dispatch(updateSelectedOffererId(Number(offererId)))
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
            hasBankAccountWithPendingCorrections: false,
            hasPendingBankAccount: false,
            hasNonFreeOffer: true,
            venuesWithNonFreeOffersWithoutBankAccounts: [],
            isActive: false,
            isValidated: false,
            managedVenues: [],
            hasActiveOffer: false,
            name: '',
            id: Number(offererId),
            postalCode: '',
            allowedOnAdage: false,
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
  }, [selectedOffererId, dispatch])

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
    // FIX ME: fixing this broke a test...
  }, [remoteConfigData?.REMOTE_CONFIG_LOADED])

  return (
    <AppLayout>
      <h1>Bienvenue dans l’espace acteurs culturels</h1>

      {seesNewNavAvailableBanner && (
        <div className={styles['beta-banner']}>
          <div className={styles['beta-banner-titles']}>
            <div className={styles['beta-banner-title']}>
              Une nouvelle interface sera bientôt disponible
            </div>
            <span>Le pass Culture se modernise pour devenir plus pratique</span>
          </div>

          <Button
            onClick={showNewNav}
            className={styles['beta-banner-activate']}
          >
            Activer dès maintenant
          </Button>
          <Button
            onClick={hideBanner}
            className={styles['beta-banner-close']}
            title="Fermer la bannière"
            variant={ButtonVariant.TERNARY}
          >
            <SvgIcon src={strokeCloseIcon} alt="" width="24" />
          </Button>
        </div>
      )}

      <div className={styles['reimbursements-banners']}>
        <AddBankAccountCallout offerer={selectedOfferer} />
        <LinkVenueCallout offerer={selectedOfferer} />
        <BankAccountHasPendingCorrectionCallout offerer={selectedOfferer} />
      </div>

      {selectedOfferer !== null && (
        <OffererBanners
          isUserOffererValidated={isUserOffererValidated}
          offerer={selectedOfferer}
        />
      )}

      {selectedOfferer?.isValidated && selectedOfferer.isActive && (
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
      {isNewNavEnabled && (
        <DialogBox
          labelledBy=""
          hasCloseButton={true}
          onDismiss={() => setIsNewNavEnabled(false)}
        >
          <h2>Bienvenue dans votre nouvelle interface</h2>
        </DialogBox>
      )}
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
