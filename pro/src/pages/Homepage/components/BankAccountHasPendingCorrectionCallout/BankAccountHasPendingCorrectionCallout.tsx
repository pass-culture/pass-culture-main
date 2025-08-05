import { GetOffererResponseModel } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { BankAccountEvents } from 'commons/core/FirebaseEvents/constants'
import { useLocation } from 'react-router'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'

export interface BankAccountHasPendingCorrectionCalloutProps {
  offerer?: GetOffererResponseModel | null
  titleOnly?: boolean
}

export const BankAccountHasPendingCorrectionCallout = ({
  offerer,
}: BankAccountHasPendingCorrectionCalloutProps): JSX.Element | null => {
  const { logEvent } = useAnalytics()
  const location = useLocation()

  const displayCallout = offerer && offerer.hasBankAccountWithPendingCorrections

  if (!displayCallout) {
    return null
  }

  return (
    <Callout
      links={[
        {
          href:
            '/remboursements/informations-bancaires?structure=' + offerer.id,
          label: 'Voir les corrections attendues',
          onClick: () => {
            logEvent(
              BankAccountEvents.CLICKED__BANK_ACCOUNT_HAS_PENDING_CORRECTIONS,
              {
                from: location.pathname,
                offererId: offerer.id,
              }
            )
          },
        },
      ]}
      variant={CalloutVariant.ERROR}
    >
      Compte bancaire incomplet
    </Callout>
  )
}
