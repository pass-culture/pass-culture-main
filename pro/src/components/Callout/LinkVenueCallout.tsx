import React from 'react'
import { useLocation } from 'react-router-dom'

import { GetOffererResponseModel } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { Callout } from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import { BankAccountEvents } from 'core/FirebaseEvents/constants'

export interface LinkVenueCalloutProps {
  offerer?: GetOffererResponseModel | null
  titleOnly?: boolean
}

export const LinkVenueCallout = ({
  offerer,
}: LinkVenueCalloutProps): JSX.Element | null => {
  const { logEvent } = useAnalytics()
  const location = useLocation()

  const displayCallout =
    offerer &&
    offerer.hasValidBankAccount &&
    offerer.venuesWithNonFreeOffersWithoutBankAccounts.length > 0

  if (!displayCallout) {
    return null
  }

  return (
    <Callout
      links={[
        {
          href:
            '/remboursements/informations-bancaires?structure=' + offerer.id,
          label: 'Gérer le rattachement de mes lieux',
          onClick: () => {
            logEvent(BankAccountEvents.CLICKED_ADD_VENUE_TO_BANK_ACCOUNT, {
              from: location.pathname,
              offererId: offerer.id,
            })
          },
        },
      ]}
      variant={CalloutVariant.ERROR}
    >
      Dernière étape pour vous faire rembourser : rattachez
      {offerer.venuesWithNonFreeOffersWithoutBankAccounts.length > 1
        ? ' vos lieux '
        : ' votre lieu '}
      à un compte bancaire
    </Callout>
  )
}
