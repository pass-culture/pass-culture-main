import React from 'react'

import { GetOffererResponseModel } from 'apiClient/v1'
import Callout from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import useActiveFeature from 'hooks/useActiveFeature'

export interface AddBankAccountCalloutProps {
  offerer?: GetOffererResponseModel | null
  titleOnly?: boolean
}

const AddBankAccountCallout = ({
  offerer = null,
  titleOnly = false,
}: AddBankAccountCalloutProps): JSX.Element | null => {
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
        },
      ]}
      type={CalloutVariant.ERROR}
      titleOnly={titleOnly}
    >
      <div>
        Rendez-vous dans l'onglet informations bancaires de votre page
        Remboursements.
      </div>
    </Callout>
  )
}

export default AddBankAccountCallout
