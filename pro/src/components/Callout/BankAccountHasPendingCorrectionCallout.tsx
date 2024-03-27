import React from 'react'
import { useLocation } from 'react-router-dom'

import { GetOffererResponseModel } from 'apiClient/v1'
import Callout from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import { BankAccountEvents } from 'core/FirebaseEvents/constants'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'

export interface BankAccountHasPendingCorrectionCalloutProps {
  offerer?: GetOffererResponseModel | null
  titleOnly?: boolean
}

const BankAccountHasPendingCorrectionCallout = ({
  offerer,
}: BankAccountHasPendingCorrectionCalloutProps): JSX.Element | null => {
  const { logEvent } = useAnalytics()
  const location = useLocation()

  const displayCallout = offerer && offerer.hasBankAccountWithPendingCorrections

  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )
  if (!isNewBankDetailsJourneyEnabled || !displayCallout) {
    return null
  }

  return (
    <Callout
      title="Compte bancaire incomplet"
      links={[
        {
          href:
            '/remboursements/informations-bancaires?structure=' + offerer.id,
          label: 'Résoudre',
          onClick: () => {
            logEvent?.(
              BankAccountEvents.CLICKED__BANK_ACCOUNT_HAS_PENDING_CORRECTIONS,
              {
                from: location.pathname,
                offererId: offerer.id,
              }
            )
          },
        },
      ]}
      variant={CalloutVariant.ERROR}
    />
  )
}

export default BankAccountHasPendingCorrectionCallout
