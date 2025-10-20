import { useMemo, useRef } from 'react'
import { useSelector } from 'react-redux'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { useOffererNamesQuery } from '@/commons/hooks/swr/useOffererNamesQuery'
import { selectCurrentOfferer } from '@/commons/store/offerer/selectors'
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

  const offererOptions = sortByLabel(
    offererNames?.map((item) => ({
      value: item.id.toString(),
      label: item.name,
    })) ?? []
  )

  const selectedOfferer = useSelector(selectCurrentOfferer)

  const hasNoVenueVisible = useMemo(() => {
    const physicalVenues = getPhysicalVenuesFromOfferer(selectedOfferer)
    const virtualVenue = getVirtualVenueFromOfferer(selectedOfferer)

    return physicalVenues.length === 0 && !virtualVenue
  }, [selectedOfferer])

  const isNotReady = offererNamesQuery.isLoading || !offererNames

  return (
    <BasicLayout mainHeading="Bienvenue sur votre espace partenaire">
      {isNotReady ? (
        <Spinner />
      ) : (
        <>
          <div className={styles['reimbursements-banners']}>
            <AddBankAccountCallout offerer={selectedOfferer} />
            <LinkVenueCallout offerer={selectedOfferer} />
            <BankAccountHasPendingCorrectionCallout offerer={selectedOfferer} />
          </div>
          {selectedOfferer && <OffererBanners offerer={selectedOfferer} />}

          {selectedOfferer?.isValidated && selectedOfferer.isActive && (
            <section className={styles.section}>
              <StatisticsDashboard offerer={selectedOfferer} />
            </section>
          )}

          <section className={styles.section} ref={offerersRef}>
            <Offerers
              selectedOfferer={selectedOfferer}
              offererOptions={offererOptions}
            />
          </section>

          {hasNoVenueVisible && selectedOfferer !== null && (
            <section className={styles['step-section']}>
              <VenueOfferSteps
                hasVenue={!hasNoVenueVisible}
                offerer={selectedOfferer}
              />
            </section>
          )}

          <section className={styles.section} ref={profileRef}>
            <div className={styles.newsletter}>
              <Newsletter />
            </div>
          </section>
        </>
      )}
    </BasicLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = Homepage
