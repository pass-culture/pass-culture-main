import { useLocation } from 'react-router'

import { GetOffererResponseModel } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { BankAccountEvents } from 'commons/core/FirebaseEvents/constants'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'

export interface LinkVenueCalloutProps {
  offerer?: GetOffererResponseModel | null
  titleOnly?: boolean
}

export const LinkVenueCallout = ({
  offerer,
}: LinkVenueCalloutProps): JSX.Element | null => {
  const { logEvent } = useAnalytics()
  const location = useLocation()
  const isOfferAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')

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
          label: `Gérer le rattachement de mes ${isOfferAddressEnabled ? 'structures' : 'lieux'}`,
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
        ? isOfferAddressEnabled
          ? ' vos structures '
          : ' vos lieux '
        : isOfferAddressEnabled
          ? ' votre structure '
          : ' votre lieu '}
      à un compte bancaire
    </Callout>
  )
}
