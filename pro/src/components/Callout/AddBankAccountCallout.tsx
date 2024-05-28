import React from 'react'
import { useLocation } from 'react-router-dom'

import { GetOffererResponseModel } from 'apiClient/v1'
import useAnalytics from 'app/App/analytics/firebase'
import { Callout } from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import { BankAccountEvents } from 'core/FirebaseEvents/constants'

interface AddBankAccountCalloutProps {
  offerer?: GetOffererResponseModel | null
}

export const AddBankAccountCallout = ({
  offerer = null,
}: AddBankAccountCalloutProps): JSX.Element | null => {
  const { logEvent } = useAnalytics()
  const location = useLocation()
  const displayBankAccountBanner =
    offerer &&
    !offerer.hasPendingBankAccount &&
    !offerer.hasValidBankAccount &&
    !offerer.hasBankAccountWithPendingCorrections &&
    offerer.venuesWithNonFreeOffersWithoutBankAccounts.length > 0

  if (!displayBankAccountBanner) {
    return null
  }

  return (
    <Callout
      links={[
        {
          href: '/remboursements/informations-bancaires',
          label: 'Ajouter un compte bancaire',
          onClick: () => {
            logEvent(BankAccountEvents.CLICKED_ADD_BANK_ACCOUNT, {
              from: location.pathname,
              offererId: offerer.id,
            })
          },
        },
      ]}
      variant={CalloutVariant.ERROR}
    >
      Aucun compte bancaire configuré pour percevoir vos remboursements
    </Callout>
  )
}
