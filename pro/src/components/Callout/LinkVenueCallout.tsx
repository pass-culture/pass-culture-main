import React from 'react'
import { useTranslation } from 'react-i18next'
import { useLocation } from 'react-router-dom'

import { GetOffererResponseModel } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { Callout } from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import { BankAccountEvents } from 'core/FirebaseEvents/constants'

export interface LinkVenueCalloutProps {
  offerer?: GetOffererResponseModel | null
  titleOnly?: boolean
}

export const LinkVenueCallout = ({
  offerer,
}: LinkVenueCalloutProps): JSX.Element | null => {
  const { t } = useTranslation('common')
  const { logEvent } = useAnalytics()
  const location = useLocation()

  const displayCallout =
    offerer &&
    offerer.hasValidBankAccount &&
    offerer.venuesWithNonFreeOffersWithoutBankAccounts.length > 0

  if (!displayCallout) {
    return null
  }

  return (
    <Callout
      links={[
        {
          href:
            '/remboursements/informations-bancaires?structure=' + offerer.id,
          label: t('manage_bank_linking'),
          onClick: () => {
            logEvent(BankAccountEvents.CLICKED_ADD_VENUE_TO_BANK_ACCOUNT, {
              from: location.pathname,
              offererId: offerer.id,
            })
          },
        },
      ]}
      variant={CalloutVariant.ERROR}
    >
      {t('last_step_reimbursement_part_one')}
      {offerer.venuesWithNonFreeOffersWithoutBankAccounts.length > 1
        ? t('last_step_reimbursement_part_two_1')
        : t('last_step_reimbursement_part_two_2')}
      {t('last_step_reimbursement_part_three')}
    </Callout>
  )
}
