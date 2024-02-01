import React from 'react'

import { GetOffererResponseModel } from 'apiClient/v1'
import Callout from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import { BankAccountEvents } from 'core/FirebaseEvents/constants'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'

export interface PendingBankAccountCalloutProps {
  offerer?: GetOffererResponseModel | null
  titleOnly?: boolean
}

const PendingBankAccountCallout = ({
  offerer,
  titleOnly = false,
}: PendingBankAccountCalloutProps): JSX.Element | null => {
  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )
  const { logEvent } = useAnalytics()
  if (!isNewBankDetailsJourneyEnabled || !offerer?.hasPendingBankAccount) {
    return null
  }

  return (
    <Callout
      title="Compte bancaire en cours de validation par nos services"
      links={
        titleOnly
          ? undefined
          : [
              {
                href: '/remboursements/informations-bancaires',
                label: 'Suivre mon dossier de compte bancaire',
                onClick: () => {
                  logEvent?.(
                    BankAccountEvents.CLICKED_BANK_DETAILS_RECORD_FOLLOW_UP,
                    {
                      from: location.pathname,
                      offererId: offerer.id,
                    }
                  )
                },
              },
            ]
      }
      variant={CalloutVariant.INFO}
    />
  )
}

export default PendingBankAccountCallout
