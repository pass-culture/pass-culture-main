import React from 'react'
import { useLocation } from 'react-router-dom'

import { GetOffererResponseModel } from 'apiClient/v1'
import Callout from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import { BankAccountEvents } from 'core/FirebaseEvents/constants'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'

export interface LinkVenueCalloutProps {
  offerer?: GetOffererResponseModel | null
  titleOnly?: boolean
}

const LinkVenueCallout = ({
  offerer,
  titleOnly = false,
}: LinkVenueCalloutProps): JSX.Element | null => {
  const { logEvent } = useAnalytics()
  const location = useLocation()

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
          href:
            '/remboursements/informations-bancaires?structure=' + offerer.id,
          linkTitle: 'Gérer le rattachement de mes lieux',
          targetLink: '',
          isExternal: false,
          onClick: () => {
            logEvent?.(BankAccountEvents.CLICKED_ADD_VENUE_TO_BANK_ACCOUNT, {
              from: location.pathname,
              offererId: offerer.id,
            })
          },
        },
      ]}
      type={CalloutVariant.ERROR}
      titleOnly={titleOnly}
    >
      <p>
        Rendez-vous dans l’onglet Informations bancaires de votre page Gestion
        financière.
      </p>
    </Callout>
  )
}

export default LinkVenueCallout
