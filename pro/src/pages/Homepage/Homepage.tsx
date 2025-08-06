import { useMemo, useRef } from 'react'
import { useSelector } from 'react-redux'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { Layout } from '@/app/App/layout/Layout'
import { GET_VENUE_TYPES_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useOfferer } from '@/commons/hooks/swr/useOfferer'
import { useOffererNamesQuery } from '@/commons/hooks/swr/useOffererNamesQuery'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'
import { sortByLabel } from '@/commons/utils/strings'
import { Newsletter } from '@/components/Newsletter/Newsletter'
import { AddBankAccountCallout } from '@/pages/Homepage/components/AddBankAccountCallout/AddBankAccountCallout'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { BankAccountHasPendingCorrectionCallout } from './components/BankAccountHasPendingCorrectionCallout/BankAccountHasPendingCorrectionCallout'
import { LinkVenueCallout } from './components/LinkVenueCallout/LinkVenueCallout'
import { OffererBanners } from './components/Offerers/components/OffererBanners/OffererBanners'
import {
  getPhysicalVenuesFromOfferer,
  getVirtualVenueFromOfferer,
} from './components/Offerers/components/VenueList/venueUtils'
import { Offerers } from './components/Offerers/Offerers'
import { StatisticsDashboard } from './components/StatisticsDashboard/StatisticsDashboard'
import { VenueOfferSteps } from './components/VenueOfferSteps/VenueOfferSteps'
import styles from './Homepage.module.scss'

export const Homepage = (): JSX.Element => {
  const profileRef = useRef<HTMLElement>(null)
  const offerersRef = useRef<HTMLElement>(null)

  const offererNamesQuery = useOffererNamesQuery()

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

  const selectedOffererId = useSelector(selectCurrentOffererId)

  // TODO: this may need to be in the store, as it is loaded in the header dropdown
  const {
    data: selectedOfferer,
    error: offererApiError,
    isLoading: isOffererLoading,
    isValidating: isOffererValidating,
  } = useOfferer(selectedOffererId, true)

  const isUserOffererValidated = !offererApiError

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
      <Layout>
        <Spinner />
      </Layout>
    )
  }

  return (
    <>
      <Layout mainHeading="Bienvenue sur votre espace partenaire">
        <div className={styles['reimbursements-banners']}>
          <AddBankAccountCallout offerer={selectedOfferer} />
          <LinkVenueCallout offerer={selectedOfferer} />
          <BankAccountHasPendingCorrectionCallout offerer={selectedOfferer} />
        </div>
        {!isOffererValidating && (selectedOfferer || offererApiError) && (
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
            isLoading={isOffererLoading}
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
          <div className={styles['newsletter']}>
            <Newsletter />
          </div>
        </section>
      </Layout>
    </>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = Homepage
