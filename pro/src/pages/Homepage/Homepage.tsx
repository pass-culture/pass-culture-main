import cn from 'classnames'
import { useMemo, useRef } from 'react'

import type { GetOffererNameResponseModel } from '@/apiClient/v1'
import type { SelectOption } from '@/commons/custom_types/form'
import { useOffererNamesQuery } from '@/commons/hooks/swr/useOffererNamesQuery'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectCurrentOfferer } from '@/commons/store/offerer/selectors'
import { sortByLabel } from '@/commons/utils/strings'
import { Newsletter } from '@/components/Newsletter/Newsletter'
import { AddBankAccountCallout } from '@/pages/Homepage/components/AddBankAccountCallout/AddBankAccountCallout'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { BankAccountHasPendingCorrectionCallout } from './components/BankAccountHasPendingCorrectionCallout/BankAccountHasPendingCorrectionCallout'
import { HighlightHome } from './components/HighlightHome/HighlightHome'
import { LinkVenueCallout } from './components/LinkVenueCallout/LinkVenueCallout'
import { OffererBanners } from './components/Offerers/components/OffererBanners/OffererBanners'
import {
  getPhysicalVenuesFromOfferer,
  getVirtualVenueFromOfferer,
} from './components/Offerers/components/VenueList/venueUtils'
import { Offerers } from './components/Offerers/Offerers'
import { PublishedOfferStats } from './components/StatisticsDashboard/components/PublishedOfferStats'
import { StatisticsDashboard } from './components/StatisticsDashboard/StatisticsDashboard'
import { VenueStatisticsDashboard } from './components/StatisticsDashboard/VenueStatisticsDashboard'
import { VenueOfferSteps } from './components/VenueOfferSteps/VenueOfferSteps'
import styles from './Homepage.module.scss'

export const Homepage = (): JSX.Element => {
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')

  const profileRef = useRef<HTMLElement>(null)
  const offerersRef = useRef<HTMLElement>(null)

  const offererNamesQuery = useOffererNamesQuery()

  const offererNamesValidated = offererNamesQuery.data

  const offererOptions = sortByLabel(
    offererNamesValidated?.map((item: GetOffererNameResponseModel) => ({
      value: item.id.toString(),
      label: item.name,
    })) ?? []
  ) as SelectOption[]

  const selectedOfferer = useAppSelector(selectCurrentOfferer)

  const selectedVenue = useAppSelector((state) => state.user.selectedVenue)

  const hasNoVenueVisible = useMemo(() => {
    const physicalVenues = getPhysicalVenuesFromOfferer(selectedOfferer)
    const virtualVenue = getVirtualVenueFromOfferer(selectedOfferer)

    return physicalVenues.length === 0 && !virtualVenue
  }, [selectedOfferer])

  const isNotReady = offererNamesQuery.isLoading || !offererNamesValidated

  const areHighlightsEnable = selectedOfferer?.canDisplayHighlights

  if (isNotReady) {
    return <Spinner />
  }

  return (
    <>
      <div className={styles['reimbursements-banners']}>
        <AddBankAccountCallout
          offerer={selectedOfferer}
          venue={selectedVenue}
        />
        <LinkVenueCallout offerer={selectedOfferer} />
        <BankAccountHasPendingCorrectionCallout
          offerer={selectedOfferer}
          venue={selectedVenue}
        />
      </div>
      {selectedOfferer && <OffererBanners offerer={selectedOfferer} />}

      {selectedOfferer?.isValidated && selectedOfferer.isActive && (
        <section className={styles.section}>
          <div className={styles['header']}>
            <h2 className={styles['title']}>
              Présence sur l’application pass Culture
            </h2>
          </div>
          <div
            className={cn(styles['container-stats'], {
              [styles['container-stats-with-highlights']]: areHighlightsEnable,
            })}
          >
            {withSwitchVenueFeature && selectedVenue ? (
              <VenueStatisticsDashboard venue={selectedVenue} />
            ) : (
              <StatisticsDashboard offerer={selectedOfferer} />
            )}
            {areHighlightsEnable && <HighlightHome />}
          </div>
          <PublishedOfferStats offerer={selectedOfferer} />
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
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = Homepage
