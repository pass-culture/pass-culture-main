import React from 'react'
import { useLocation } from 'react-router-dom'

import { GetOffererResponseModel } from 'apiClient/v1'
import Callout from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import { BankAccountEvents } from 'core/FirebaseEvents/constants'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'

interface AddBankAccountCalloutProps {
  offerer?: GetOffererResponseModel | null
}

const AddBankAccountCallout = ({
  offerer = null,
}: AddBankAccountCalloutProps): JSX.Element | null => {
  const { logEvent } = useAnalytics()
  const location = useLocation()
  const displayBankAccountBanner =
    offerer &&
    !offerer.hasPendingBankAccount &&
    !offerer.hasValidBankAccount &&
    offerer.venuesWithNonFreeOffersWithoutBankAccounts.length > 0

  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )
  if (!isNewBankDetailsJourneyEnabled || !displayBankAccountBanner) {
    return null
  }

  return (
    <Callout
      links={[
        {
          href: '/remboursements/informations-bancaires',
          label: 'Ajouter un compte bancaire',
          onClick: () => {
            logEvent?.(BankAccountEvents.CLICKED_ADD_BANK_ACCOUNT, {
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

export default AddBankAccountCallout
