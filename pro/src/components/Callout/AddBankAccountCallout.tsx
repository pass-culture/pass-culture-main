import React from 'react'

import Callout from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import useActiveFeature from 'hooks/useActiveFeature'

export interface AddBankAccountCalloutProps {
  titleOnly?: boolean
}

const AddBankAccountCallout = ({
  titleOnly = false,
}: AddBankAccountCalloutProps): JSX.Element | null => {
  const isNewBankDetailsJourneyEnable = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )
  if (!isNewBankDetailsJourneyEnable) {
    return null
  }

  return (
    <Callout
      title="Ajoutez un compte bancaire pour percevoir vos remboursements"
      links={[
        {
          href: '/remboursements/informations-bancaires',
          linkTitle: 'ajouter un compte bancaire',
        },
      ]}
      type={CalloutVariant.ERROR}
      titleOnly={titleOnly}
    >
      <div>
        Rendez-vous dans l'onglet informations bancaires de votre page
        Remboursements
      </div>
    </Callout>
  )
}

export default AddBankAccountCallout
