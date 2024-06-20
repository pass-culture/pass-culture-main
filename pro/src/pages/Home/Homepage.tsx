import React, { useMemo, useRef, useState } from 'react'
import { useDispatch } from 'react-redux'
import { useSearchParams } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { AppLayout } from 'app/AppLayout'
import { AddBankAccountCallout } from 'components/Callout/AddBankAccountCallout'
import { BankAccountHasPendingCorrectionCallout } from 'components/Callout/BankAccountHasPendingCorrectionCallout'
import { LinkVenueCallout } from 'components/Callout/LinkVenueCallout'
import { Newsletter } from 'components/Newsletter/Newsletter'
import { TutorialDialog } from 'components/TutorialDialog/TutorialDialog'
import {
  GET_OFFERER_NAMES_QUERY_KEY,
  GET_OFFERER_QUERY_KEY,
  GET_VENUE_TYPES_QUERY_KEY,
} from 'config/swrQueryKeys'
import { hasStatusCode } from 'core/OfferEducational/utils/hasStatusCode'
import { SAVED_OFFERER_ID_KEY } from 'core/shared/constants'
import { useCurrentUser } from 'hooks/useCurrentUser'
import { useIsNewInterfaceActive } from 'hooks/useIsNewInterfaceActive'
import { useNotification } from 'hooks/useNotification'
import strokeCloseIcon from 'icons/stroke-close.svg'
import { WelcomeToTheNewBetaBanner } from 'pages/Home/WelcomeToTheNewBetaBanner/WelcomeToTheNewBetaBanner'
import { HTTP_STATUS } from 'repository/pcapi/pcapiClient'
import { updateSelectedOffererId, updateUser } from 'store/user/reducer'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Spinner } from 'ui-kit/Spinner/Spinner'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { formatBrowserTimezonedDateAsUTC, isDateValid } from 'utils/date'
import { getSavedOffererId } from 'utils/getSavedOffererId'
import { localStorageAvailable } from 'utils/localStorageAvailable'
import { sortByLabel } from 'utils/strings'

import screen from './assets/screen.gif'
import styles from './Homepage.module.scss'
import { OffererBanners } from './Offerers/OffererBanners'
import { Offerers } from './Offerers/Offerers'
import { ProfileAndSupport } from './ProfileAndSupport/ProfileAndSupport'
import { StatisticsDashboard } from './StatisticsDashboard/StatisticsDashboard'
import { VenueOfferSteps } from './VenueOfferSteps/VenueOfferSteps'
import {
  getPhysicalVenuesFromOfferer,
  getVirtualVenueFromOfferer,
} from './venueUtils'

const HAS_CLOSED_BETA_TEST_BANNER = 'HAS_CLOSED_BETA_TEST_BANNER'

export const Homepage = (): JSX.Element => {
  const dispatch = useDispatch()
  const hasNewSideBarNavigation = useIsNewInterfaceActive()
  const { currentUser } = useCurrentUser()
  const notify = useNotification()
  const [searchParams] = useSearchParams()
  const profileRef = useRef<HTMLElement>(null)
  const offerersRef = useRef<HTMLElement>(null)

  const userClosedBetaTestBanner = localStorageAvailable()
    ? !localStorage.getItem(HAS_CLOSED_BETA_TEST_BANNER)
    : true
  const isEligibleToNewNav =
    isDateValid(currentUser.navState?.eligibilityDate) &&
    new Date(currentUser.navState.eligibilityDate) <=
      new Date(formatBrowserTimezonedDateAsUTC(new Date()))

  const [isNewNavEnabled, setIsNewNavEnabled] = useState(false)
  const [seesNewNavAvailableBanner, setSeesNewNavAvailableBanner] = useState(
    userClosedBetaTestBanner && !hasNewSideBarNavigation && isEligibleToNewNav
  )

  const offererNamesQuery = useSWR([GET_OFFERER_NAMES_QUERY_KEY], () =>
    api.listOfferersNames()
  )
  const offererNames = offererNamesQuery.data?.offerersNames

  const venueTypesQuery = useSWR([GET_VENUE_TYPES_QUERY_KEY], () =>
    api.getVenueTypes()
  )
  const venueTypes = venueTypesQuery.data

  const offererOptions = sortByLabel(
    offererNames?.map((item) => ({
      value: item['id'].toString(),
      label: item['name'],
    })) ?? []
  )

  const selectedOffererId =
    // TODO remove this when noUncheckedIndexedAccess is enabled in TS config
    // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition
    searchParams.get('structure') ??
    getSavedOffererId(offererOptions) ??
    offererOptions[0]?.value ??
    ''

  const selectedOffererQuery = useSWR(
    offererNames ? [GET_OFFERER_QUERY_KEY, selectedOffererId] : null,
    async ([, offererIdParam]) => {
      try {
        const offerer = await api.getOfferer(Number(offererIdParam))
        localStorage.setItem(SAVED_OFFERER_ID_KEY, offererIdParam)
        dispatch(updateSelectedOffererId(Number(offererIdParam)))

        return offerer
      } catch (error) {
        if (hasStatusCode(error) && error.status === HTTP_STATUS.FORBIDDEN) {
          throw error
        }
        return null
      }
    },
    {
      fallbackData: null,
      shouldRetryOnError: false,
      onError: () => {},
    }
  )
  const selectedOfferer = selectedOffererQuery.data
  const isUserOffererValidated = !selectedOffererQuery.error

  const hasNoVenueVisible = useMemo(() => {
    const physicalVenues = getPhysicalVenuesFromOfferer(selectedOfferer)
    const virtualVenue = getVirtualVenueFromOfferer(selectedOfferer)

    return physicalVenues.length === 0 && !virtualVenue
  }, [selectedOfferer])

  if (
    offererNamesQuery.isLoading ||
    venueTypesQuery.isLoading ||
    !offererNames ||
    !venueTypes
  ) {
    return (
      <AppLayout>
        <Spinner />
      </AppLayout>
    )
  }

  async function showNewNav() {
    try {
      await api.postNewProNav()
      setSeesNewNavAvailableBanner(false)
      dispatch(
        updateUser({
          ...currentUser,
          navState: {
            newNavDate: formatBrowserTimezonedDateAsUTC(new Date()),
            eligibilityDate: currentUser.navState?.eligibilityDate,
          },
        })
      )
      setIsNewNavEnabled(true)
    } catch (error) {
      notify.error("Impossible de réaliser l'action. Réessayez plus tard")
    }
  }

  function hideBanner() {
    localStorageAvailable() &&
      localStorage.setItem(HAS_CLOSED_BETA_TEST_BANNER, 'true')
    setSeesNewNavAvailableBanner(false)
  }

  return (
    <AppLayout>
      <h1>Bienvenue dans l’espace acteurs culturels</h1>

      {seesNewNavAvailableBanner && (
        <div className={styles['beta-banner']}>
          <div className={styles['beta-banner-left']}>
            <div className={styles['beta-banner-titles']}>
              <div className={styles['beta-banner-title']}>
                Une nouvelle interface sera bientôt disponible
              </div>
              <span>
                Le pass Culture se modernise pour devenir plus pratique
              </span>
            </div>

            <Button
              onClick={showNewNav}
              className={styles['beta-banner-activate']}
            >
              Activer dès maintenant
            </Button>
          </div>
          <div className={styles['beta-banner-right']}>
            <img src={screen} alt="" />
          </div>
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
      {!selectedOffererQuery.isValidating &&
        (selectedOffererQuery.data || selectedOffererQuery.error) && (
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
          isLoading={selectedOffererQuery.isLoading}
          offererOptions={offererOptions}
          isUserOffererValidated={isUserOffererValidated}
          venueTypes={venueTypes}
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
        {!hasNewSideBarNavigation && <ProfileAndSupport />}

        <div className={styles['newsletter']}>
          <Newsletter />
        </div>
      </section>

      <TutorialDialog />
      {isNewNavEnabled && hasNewSideBarNavigation && (
        <WelcomeToTheNewBetaBanner setIsNewNavEnabled={setIsNewNavEnabled} />
      )}
    </AppLayout>
  )
}

export const HomeTestTypo = () => (
  <>
    <h1>Test typo</h1>
    <h2>Test title 2</h2>
    <h3>Test title 3</h3>
    <p>Test text</p>
  </>
)

// Below exports are used by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Homepage
