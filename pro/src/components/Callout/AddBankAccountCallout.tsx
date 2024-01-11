import React from 'react'
import { useLocation } from 'react-router-dom'

import { GetOffererResponseModel } from 'apiClient/v1'
import Callout from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import { BankAccountEvents } from 'core/FirebaseEvents/constants'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'

export interface AddBankAccountCalloutProps {
  offerer?: GetOffererResponseModel | null
  titleOnly?: boolean
}

const AddBankAccountCallout = ({
  offerer = null,
  titleOnly = false,
}: AddBankAccountCalloutProps): JSX.Element | null => {
  const { logEvent } = useAnalytics()
  const location = useLocation()
  const displayBankAccountBanner =
    offerer &&
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
      title="Ajoutez un compte bancaire pour percevoir vos remboursements"
      links={[
        {
          href: '/remboursements/informations-bancaires',
          linkTitle: 'Ajouter un compte bancaire',
          targetLink: '',
          isExternal: false,
          onClick: () => {
            logEvent?.(BankAccountEvents.CLICKED_ADD_BANK_ACCOUNT, {
              from: location.pathname,
              offererId: offerer.id,
            })
          },
        },
      ]}
      type={CalloutVariant.ERROR}
      titleOnly={titleOnly}
    >
      <div>
        Rendez-vous dans l’onglet informations bancaires de votre page Gestion
        financière.
      </div>
    </Callout>
  )
}

export default AddBankAccountCallout
