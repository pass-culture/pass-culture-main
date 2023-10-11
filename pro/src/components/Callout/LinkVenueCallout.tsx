import React from 'react'

import { GetOffererResponseModel } from 'apiClient/v1'
import Callout from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import useActiveFeature from 'hooks/useActiveFeature'

export interface LinkVenueCalloutProps {
  offerer?: GetOffererResponseModel | null
  titleOnly?: boolean
}

const LinkVenueCallout = ({
  offerer,
  titleOnly = false,
}: LinkVenueCalloutProps): JSX.Element | null => {
  const displayCallout =
    offerer &&
    offerer.hasValidBankAccount &&
    offerer.venuesWithNonFreeOffersWithoutBankAccounts.length > 0

  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )
  if (!isNewBankDetailsJourneyEnabled || !displayCallout) {
    return null
  }

  return (
    <Callout
      title={`Dernière étape pour vous faire rembourser : rattachez ${
        offerer?.venuesWithNonFreeOffersWithoutBankAccounts.length > 1
          ? 'vos lieux'
          : 'votre lieu'
      } à un compte bancaire`}
      links={[
        {
          href: '/remboursements/informations-bancaires',
          linkTitle: 'Gérer le rattachement de mes lieux',
          targetLink: '',
          isExternal: false,
        },
      ]}
      type={CalloutVariant.ERROR}
      titleOnly={titleOnly}
    >
      <p>
        Afin de percevoir vos remboursements, vous devez rattacher
        {offerer?.venuesWithNonFreeOffersWithoutBankAccounts.length > 1
          ? ' vos lieux'
          : ' votre lieu'}{' '}
        à un compte bancaire. Les offres dont les lieux ne sont pas rattachés à
        un compte bancaire ne seront pas remboursées.
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
