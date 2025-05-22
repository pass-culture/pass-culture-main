import { useRef, useState } from 'react'
import { useSelector } from 'react-redux'
import { useLocation, useOutletContext } from 'react-router'
import useSWR, { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { BankAccountResponseModel } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import {
  GET_OFFERER_BANKACCOUNTS_AND_ATTACHED_VENUES,
  GET_OFFERER_QUERY_KEY,
} from 'commons/config/swrQueryKeys'
import { BankAccountEvents } from 'commons/core/FirebaseEvents/constants'
import { useNotification } from 'commons/hooks/useNotification'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { ReimbursementBankAccount } from 'components/ReimbursementBankAccount/ReimbursementBankAccount'
import fullMoreIcon from 'icons/full-more.svg'
import { LinkVenuesDialog } from 'pages/Reimbursements/BankInformations/LinkVenuesDialog'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { ReimbursementsContextProps } from '../Reimbursements'

import { AddBankInformationsDialog } from './AddBankInformationsDialog'
import styles from './BankInformations.module.scss'

export const BankInformations = (): JSX.Element => {
  const notify = useNotification()
  const { logEvent } = useAnalytics()
  const location = useLocation()
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const { mutate } = useSWRConfig()

  const [showAddBankInformationsDialog, setShowAddBankInformationsDialog] =
    useState(false)

  const addBankAccountButtonRef = useRef<HTMLButtonElement>(null)

  const {
    selectedOfferer = null,
    // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition
  }: ReimbursementsContextProps = useOutletContext() ?? {}
  const [selectedBankAccount, setSelectedBankAccount] =
    useState<BankAccountResponseModel | null>(null)

  const bankAccountVenuesQuery = useSWR(
    [GET_OFFERER_BANKACCOUNTS_AND_ATTACHED_VENUES, selectedOffererId],
    ([, offererId]) =>
      api.getOffererBankAccountsAndAttachedVenues(Number(offererId)),
    {
      onError: () =>
        notify.error(
          'Impossible de récupérer les informations relatives à vos comptes bancaires.'
        ),
    }
  )

  if (bankAccountVenuesQuery.isLoading) {
    return <Spinner />
  }

  const updateOfferer = async (offererId: number) => {
    if (offererId) {
      await mutate([
        GET_OFFERER_BANKACCOUNTS_AND_ATTACHED_VENUES,
        Number(offererId),
      ])
      await mutate([GET_OFFERER_QUERY_KEY, Number(offererId)])
    }
  }

  async function closeDialog(update?: boolean) {
    if (selectedOffererId) {
      if (update) {
        await updateOfferer(selectedOffererId)
      }
      setSelectedBankAccount(null)
    }
  }

  let bankAccountVenues = bankAccountVenuesQuery.data?.managedVenues

  const updateBankAccountVenuePricingPoint = (venueId: number) => {
    if (!bankAccountVenuesQuery.data) {
      return
    }
    void bankAccountVenuesQuery.mutate(
      {
        ...bankAccountVenuesQuery.data,
        managedVenues: bankAccountVenuesQuery.data.managedVenues.map((venue) =>
          venue.id === venueId ? { ...venue, hasPricingPoint: true } : venue
        ),
      },
      { revalidate: false }
    )
  }

  const selectedOffererBankAccounts = bankAccountVenuesQuery.data

  return (
    <>
      <div className={styles['information']}>
        {!selectedOfferer?.hasValidBankAccount &&
          !selectedOfferer?.hasPendingBankAccount &&
          'Ajoutez au moins un compte bancaire pour percevoir vos remboursements.'}

        {(selectedOfferer?.hasValidBankAccount ||
          selectedOfferer?.hasPendingBankAccount) && (
          <>
            Vous pouvez ajouter plusieurs comptes bancaires afin de percevoir
            les remboursements de vos offres. Chaque compte bancaire fera
            l’objet d’un remboursement et d’un justificatif de remboursement
            distincts. <br />
          </>
        )}
      </div>
      {selectedOffererBankAccounts &&
        selectedOffererBankAccounts.bankAccounts.length > 0 && (
          <div className={styles['bank-accounts']}>
            {selectedOffererBankAccounts.bankAccounts.map((bankAccount) => (
              <ReimbursementBankAccount
                bankAccount={bankAccount}
                offererId={selectedOfferer?.id}
                key={bankAccount.id}
                onUpdateButtonClick={(bankAccountId) => {
                  setSelectedBankAccount(
                    selectedOffererBankAccounts.bankAccounts.find(
                      (bankAccount) => bankAccount.id === bankAccountId
                    ) ?? null
                  )
                }}
                managedVenues={selectedOffererBankAccounts.managedVenues}
                hasWarning={
                  (selectedOfferer &&
                    selectedOfferer.venuesWithNonFreeOffersWithoutBankAccounts
                      .length > 0) ??
                  false
                }
              />
            ))}
          </div>
        )}
      <Button
        icon={fullMoreIcon}
        className={styles['add-bank-account-button']}
        variant={
          /* istanbul ignore next : graphic changes */ selectedOfferer &&
          (selectedOfferer.hasPendingBankAccount ||
            selectedOfferer.hasValidBankAccount)
            ? ButtonVariant.SECONDARY
            : ButtonVariant.PRIMARY
        }
        onClick={() => {
          setShowAddBankInformationsDialog(true)
          logEvent(BankAccountEvents.CLICKED_ADD_BANK_ACCOUNT, {
            from: location.pathname,
            offererId: selectedOfferer?.id,
          })
        }}
        ref={addBankAccountButtonRef}
      >
        Ajouter un compte bancaire
      </Button>
      <AddBankInformationsDialog
        closeDialog={() => {
          setShowAddBankInformationsDialog(false)
        }}
        offererId={selectedOfferer?.id}
        isDialogOpen={showAddBankInformationsDialog}
        dialogTriggerRef={addBankAccountButtonRef}
      />
      {selectedBankAccount !== null && selectedOfferer !== null && (
        <LinkVenuesDialog
          offererId={selectedOfferer.id}
          selectedBankAccount={selectedBankAccount}
          managedVenues={bankAccountVenues ?? []}
          updateBankAccountVenuePricingPoint={
            updateBankAccountVenuePricingPoint
          }
          closeDialog={closeDialog}
        />
      )}
    </>
  )
}
