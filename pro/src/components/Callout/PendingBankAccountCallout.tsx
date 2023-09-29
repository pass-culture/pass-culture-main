import React from 'react'

import Callout from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import useActiveFeature from 'hooks/useActiveFeature'

export interface PendingBankAccountCalloutProps {
  titleOnly?: boolean
}

const PendingBankAccountCallout = ({
  titleOnly = false,
}: PendingBankAccountCalloutProps): JSX.Element | null => {
  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )
  if (!isNewBankDetailsJourneyEnabled) {
    return null
  }

  return (
    <Callout
      title="Compte bancaire en cours de validation par nos services"
      links={[
        {
          href: '/remboursements/informations-bancaires',
          linkTitle: 'Suivre mon dossier de compte bancaire',
        },
      ]}
      type={CalloutVariant.INFO}
      titleOnly={titleOnly}
    />
  )
}

export default PendingBankAccountCallout
