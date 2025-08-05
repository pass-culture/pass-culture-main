import { GetOffererResponseModel } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { BankAccountEvents } from 'commons/core/FirebaseEvents/constants'
import { useLocation } from 'react-router'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'

interface AddBankAccountCalloutProps {
  offerer?: GetOffererResponseModel | null
}

export const AddBankAccountCallout = ({
  offerer = null,
}: AddBankAccountCalloutProps): JSX.Element | null => {
  const { logEvent } = useAnalytics()
  const location = useLocation()
  const displayBankAccountBanner =
    offerer &&
    !offerer.hasPendingBankAccount &&
    !offerer.hasValidBankAccount &&
    !offerer.hasBankAccountWithPendingCorrections &&
    offerer.venuesWithNonFreeOffersWithoutBankAccounts.length > 0

  if (!displayBankAccountBanner) {
    return null
  }

  return (
    <Callout
      links={[
        {
          href: '/remboursements/informations-bancaires',
          label: 'Ajouter un compte bancaire',
          onClick: () => {
            logEvent(BankAccountEvents.CLICKED_ADD_BANK_ACCOUNT, {
              from: location.pathname,
              offererId: offerer.id,
            })
          },
        },
      ]}
      variant={CalloutVariant.ERROR}
    >
      Aucun compte bancaire configuré pour percevoir vos remboursements
    </Callout>
  )
}
