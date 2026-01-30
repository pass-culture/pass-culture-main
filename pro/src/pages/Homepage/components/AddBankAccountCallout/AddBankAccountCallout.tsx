import { useLocation } from 'react-router'

import type {
  GetOffererResponseModel,
  GetVenueResponseModel,
} from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { BankAccountEvents } from '@/commons/core/FirebaseEvents/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import fullNextIcon from '@/icons/full-next.svg'

import styles from '../../Homepage.module.scss'

interface AddBankAccountCalloutProps {
  offerer?: GetOffererResponseModel | null
  venue?: GetVenueResponseModel | null
}

export const AddBankAccountCallout = ({
  offerer = null,
  venue = null,
}: AddBankAccountCalloutProps): JSX.Element | null => {
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')
  const { logEvent } = useAnalytics()
  const location = useLocation()

  let displayBankAccountBanner: boolean | null

  if (withSwitchVenueFeature) {
    displayBankAccountBanner =
      venue && venue.hasNonFreeOffers && !venue.bankAccountStatus
  } else {
    displayBankAccountBanner =
      offerer &&
      !offerer.hasPendingBankAccount &&
      !offerer.hasValidBankAccount &&
      !offerer.hasBankAccountWithPendingCorrections &&
      offerer.venuesWithNonFreeOffersWithoutBankAccounts.length > 0
  }

  if (!displayBankAccountBanner) {
    return null
  }

  return (
    <div className={styles['reimbursements-banner']}>
      <Banner
        title={
          withSwitchVenueFeature
            ? 'Aucun compte bancaire configuré pour percevoir vos remboursements'
            : 'Compte bancaire manquant'
        }
        variant={BannerVariants.ERROR}
        actions={[
          {
            href: '/remboursements/informations-bancaires',
            label: 'Ajouter un compte bancaire',
            type: 'link',
            icon: fullNextIcon,
            onClick: () => {
              logEvent(BankAccountEvents.CLICKED_ADD_BANK_ACCOUNT, {
                from: location.pathname,
                ...(!withSwitchVenueFeature && { offererId: offerer?.id }),
                ...(withSwitchVenueFeature && { venueId: venue?.id }),
              })
            },
          },
        ]}
        description={
          withSwitchVenueFeature
            ? ''
            : 'Configurez un compte bancaire pour recevoir vos remboursements.'
        }
      />
    </div>
  )
}
