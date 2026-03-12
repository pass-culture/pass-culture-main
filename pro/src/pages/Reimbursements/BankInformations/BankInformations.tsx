import classNames from 'classnames'
import { useRef, useState } from 'react'
import { useLocation } from 'react-router'
import useSWR, { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import type { BankAccountResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import {
  GET_OFFERER_BANK_ACCOUNTS_AND_ATTACHED_VENUES_QUERY_KEY,
  GET_OFFERER_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { BankAccountEvents } from '@/commons/core/FirebaseEvents/constants'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { setSelectedVenue } from '@/commons/store/user/reducer'
import { ReimbursementBankAccount } from '@/components/ReimbursementBankAccount/ReimbursementBankAccount'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import fullMoreIcon from '@/icons/full-more.svg'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { AddBankInformationsDialog } from './AddBankInformationsDialog/AddBankInformationsDialog'
import styles from './BankInformations.module.scss'
import { LinkVenuesDialog } from './LinkVenuesDialog/LinkVenuesDialog'

const BankInformations = (): JSX.Element => {
  const snackBar = useSnackBar()
  const { logEvent } = useAnalytics()
  const location = useLocation()
  const { mutate } = useSWRConfig()
  const dispatch = useAppDispatch()
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')
  const currentOfferer = useAppSelector((state) => state.offerer.currentOfferer)
  const adminSelectedOfferer = useAppSelector(
    (store) => store.user.selectedAdminOfferer
  )
  const selectedVenue = useAppSelector((store) => store.user.selectedVenue)

  const selectedOfferer = withSwitchVenueFeature
    ? adminSelectedOfferer
    : currentOfferer
  assertOrFrontendError(selectedOfferer, '`selectedOfferer` is undefined')

  const offererId = selectedOfferer.id

  const [showAddBankInformationsDialog, setShowAddBankInformationsDialog] =
    useState(false)

  const addBankAccountButtonRef = useRef<HTMLButtonElement>(null)
  const editBankAccountDialogTriggerRef = useRef<HTMLButtonElement>(null)

  const [selectedBankAccount, setSelectedBankAccount] =
    useState<BankAccountResponseModel | null>(null)

  const bankAccountVenuesQuery = useSWR(
    [GET_OFFERER_BANK_ACCOUNTS_AND_ATTACHED_VENUES_QUERY_KEY, offererId],
    ([, offererId]) =>
      api.getOffererBankAccountsAndAttachedVenues(Number(offererId)),
    {
      onError: () =>
        snackBar.error(
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
        GET_OFFERER_BANK_ACCOUNTS_AND_ATTACHED_VENUES_QUERY_KEY,
        Number(offererId),
      ])
      await mutate([GET_OFFERER_QUERY_KEY, Number(offererId)])
    }
  }

  async function closeDialog(update?: boolean) {
    if (offererId) {
      if (update) {
        await updateOfferer(offererId)

        if (selectedVenue) {
          // Direct API call without SWR mutate because no useSWR(GET_VENUE_QUERY_KEY)
          // is mounted on this page, so mutate(key) would not trigger any
          // revalidation (see https://swr.vercel.app/docs/mutation#global-mutate)
          const updatedVenue = await api.getVenue(selectedVenue.id)
          dispatch(setSelectedVenue(updatedVenue))
        }
      }
      setSelectedBankAccount(null)
    }
  }

  const bankAccountVenues = bankAccountVenuesQuery.data?.managedVenues

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
    <div className={styles['bank-information']}>
      <div>
        {selectedOfferer.hasValidBankAccount ||
        selectedOfferer.hasPendingBankAccount ? (
          <p>
            Vous pouvez ajouter plusieurs comptes bancaires afin de percevoir
            les remboursements de vos offres. Chaque compte bancaire fera
            l’objet d’un remboursement et d’un justificatif de remboursement
            distincts.
          </p>
        ) : (
          <p>
            Ajoutez au moins un compte bancaire pour percevoir vos
            remboursements.
          </p>
        )}
      </div>

      <Button
        icon={fullMoreIcon}
        variant={
          selectedOfferer.hasPendingBankAccount ||
          selectedOfferer.hasValidBankAccount
            ? ButtonVariant.SECONDARY
            : ButtonVariant.PRIMARY
        }
        onClick={() => {
          setShowAddBankInformationsDialog(true)
          logEvent(BankAccountEvents.CLICKED_ADD_BANK_ACCOUNT, {
            from: location.pathname,
            offererId: selectedOfferer.id,
          })
        }}
        ref={addBankAccountButtonRef}
        label="Ajouter un compte bancaire"
      />

      {selectedOffererBankAccounts &&
        selectedOffererBankAccounts.bankAccounts.length > 0 && (
          <div
            className={classNames(
              styles['bank-information'],
              styles['bank-information-panels']
            )}
          >
            {selectedOffererBankAccounts.bankAccounts.map((bankAccount) => (
              <ReimbursementBankAccount
                bankAccount={bankAccount}
                offererId={selectedOfferer.id}
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
                  selectedOfferer.venuesWithNonFreeOffersWithoutBankAccounts
                    .length > 0
                }
                updateButtonRef={editBankAccountDialogTriggerRef}
              />
            ))}
          </div>
        )}

      <AddBankInformationsDialog
        closeDialog={() => {
          setShowAddBankInformationsDialog(false)
        }}
        offererId={selectedOfferer.id}
        isDialogOpen={showAddBankInformationsDialog}
        dialogTriggerRef={addBankAccountButtonRef}
      />
      {selectedBankAccount !== null && (
        <LinkVenuesDialog
          offererId={selectedOfferer.id}
          selectedBankAccount={selectedBankAccount}
          managedVenues={bankAccountVenues ?? []}
          editBankAccountDialogTriggerRef={editBankAccountDialogTriggerRef}
          updateBankAccountVenuePricingPoint={
            updateBankAccountVenuePricingPoint
          }
          closeDialog={closeDialog}
        />
      )}
    </div>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = BankInformations
