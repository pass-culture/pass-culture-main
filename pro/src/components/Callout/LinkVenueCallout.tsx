import React from 'react'

import Callout from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import useActiveFeature from 'hooks/useActiveFeature'

export interface LinkVenueCalloutProps {
  titleOnly?: boolean
  hasMultipleVenuesToLink?: boolean
}

const LinkVenueCallout = ({
  titleOnly = false,
  hasMultipleVenuesToLink = false,
}: LinkVenueCalloutProps): JSX.Element | null => {
  const isNewBankDetailsJourneyEnable = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )
  if (!isNewBankDetailsJourneyEnable) {
    return null
  }

  return (
    <Callout
      title={`Dernière étape pour vous faire rembourser : rattachez ${
        hasMultipleVenuesToLink ? 'vos lieux' : 'votre lieu'
      } à un compte bancaire`}
      links={[
        {
          href: '/remboursements/informations-bancaires',
          linkTitle: 'Gérer le rattachement de mes lieux',
          targetLink: '',
        },
      ]}
      type={CalloutVariant.ERROR}
      titleOnly={titleOnly}
    >
      <p>
        Afin de percevoir vos remboursements, vous devez rattacher
        {hasMultipleVenuesToLink ? ' vos lieux' : ' votre lieu'} à un compte
        bancaire. Les offres dont les lieux ne sont pas rattachés à un compte
        bancaire ne seront pas remboursées.
      </p>
      <br />
      <p>
        Rendez-vous dans l'onglet informations bancaires de votre page
        Remboursements.
      </p>
    </Callout>
  )
}

export default LinkVenueCallout
