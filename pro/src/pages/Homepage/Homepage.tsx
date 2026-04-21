import cn from 'classnames'
import { useRef } from 'react'

import { SimplifiedBankAccountStatus } from '@/apiClient/v1'
import { useOffererNamesQuery } from '@/commons/hooks/swr/useOffererNamesQuery'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { Newsletter } from '@/components/Newsletter/Newsletter'
import { AddBankAccountCallout } from '@/pages/Homepage/components/AddBankAccountCallout/AddBankAccountCallout'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { BankAccountHasPendingCorrectionCallout } from './components/BankAccountHasPendingCorrectionCallout/BankAccountHasPendingCorrectionCallout'
import { HighlightHome } from './components/HighlightHome/HighlightHome'
import { PartnerPage } from './components/Offerers/components/PartnerPages/components/PartnerPage'
import { PublishedOfferStats } from './components/StatisticsDashboard/components/PublishedOfferStats'
import { StatisticsDashboard } from './components/StatisticsDashboard/StatisticsDashboard'
import styles from './Homepage.module.scss'

export const Homepage = (): JSX.Element => {
  const profileRef = useRef<HTMLElement>(null)
  const offerersRef = useRef<HTMLElement>(null)

  const offererNamesQuery = useOffererNamesQuery()

  const offererNamesValidated = offererNamesQuery.data

  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  const isNotReady = offererNamesQuery.isLoading || !offererNamesValidated
  const shouldDisplayBankAccountCallout =
    selectedPartnerVenue.hasNonFreeOffers &&
    !selectedPartnerVenue.bankAccountStatus
  const shouldDisplayBankAccountHasPendingCorrectionCallout =
    selectedPartnerVenue.hasNonFreeOffers &&
    selectedPartnerVenue.bankAccountStatus ===
      SimplifiedBankAccountStatus.PENDING_CORRECTIONS

  if (isNotReady) {
    return <Spinner />
  }

  return (
    <>
      <div className={styles['reimbursements-banners']}>
        {shouldDisplayBankAccountCallout && (
          <AddBankAccountCallout venue={selectedPartnerVenue} />
        )}
        {shouldDisplayBankAccountHasPendingCorrectionCallout && (
          <BankAccountHasPendingCorrectionCallout
            venue={selectedPartnerVenue}
          />
        )}
      </div>

      <section className={styles.section}>
        <div className={styles['header']}>
          <h2 className={styles['title']}>
            Présence sur l’application pass Culture
          </h2>
        </div>
        <div
          className={cn(styles['container-stats'], {
            [styles['container-stats-with-highlights']]:
              selectedPartnerVenue.canDisplayHighlights,
          })}
        >
          <StatisticsDashboard venue={selectedPartnerVenue} />
          {selectedPartnerVenue.canDisplayHighlights && <HighlightHome />}
        </div>
        <PublishedOfferStats />
      </section>

      <section className={styles.section} ref={offerersRef}>
        <PartnerPage />
      </section>

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
