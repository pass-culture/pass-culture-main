import React, { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  BankAccountResponseModel,
  GetOffererBankAccountsResponseModel,
  ManagedVenues,
} from 'apiClient/v1'
import ReimbursementBankAccount from 'components/ReimbursementBankAccount/ReimbursementBankAccount'
import { useReimbursementContext } from 'context/ReimbursementContext/ReimbursementContext'
import { BankAccountEvents } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import fullLinkIcon from 'icons/full-link.svg'
import fullMoreIcon from 'icons/full-more.svg'
import LinkVenuesDialog from 'pages/Reimbursements/BankInformations/LinkVenuesDialog'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Spinner from 'ui-kit/Spinner/Spinner'

import AddBankInformationsDialog from './AddBankInformationsDialog'
import styles from './BankInformations.module.scss'

const BankInformations = (): JSX.Element => {
  const notify = useNotification()
  const { logEvent } = useAnalytics()
  const location = useLocation()

  const [showAddBankInformationsDialog, setShowAddBankInformationsDialog] =
    useState(false)
  const { selectedOfferer } = useReimbursementContext()

  const [isOffererBankAccountsLoading, setIsOffererBankAccountsLoading] =
    useState<boolean>(false)
  const [selectedOffererBankAccounts, setSelectedOffererBankAccounts] =
    useState<GetOffererBankAccountsResponseModel | null>(null)
  const [selectedBankAccount, setSelectedBankAccount] =
    useState<BankAccountResponseModel | null>(null)
  const [bankAccountVenues, setBankAccountVenues] = useState<
    Array<ManagedVenues>
  >([])

  useEffect(() => {
    const getSelectedOffererBankAccounts = async (
      selectedOffererId: number
    ) => {
      setIsOffererBankAccountsLoading(true)
      try {
        const offererBankAccounts =
          await api.getOffererBankAccountsAndAttachedVenues(selectedOffererId)
        setSelectedOffererBankAccounts(offererBankAccounts)
        setBankAccountVenues(offererBankAccounts.managedVenues)
        setIsOffererBankAccountsLoading(false)
      } catch (error) {
        notify.error(
          'Impossible de récupérer les informations relatives à vos comptes bancaires.'
        )
      } finally {
        setIsOffererBankAccountsLoading(false)
      }
    }

    selectedOfferer && void getSelectedOffererBankAccounts(selectedOfferer.id)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedOfferer])

  if (isOffererBankAccountsLoading) {
    return <Spinner />
  }

  function closeDialog() {
    if (selectedOfferer !== null) {
      setSelectedBankAccount(null)
    }
  }

  const updateBankAccountVenuePricingPoint = (venueId: number) => {
    setBankAccountVenues(
      bankAccountVenues.map((venue) =>
        venue.id === venueId ? { ...venue, hasPricingPoint: true } : venue
      )
    )
  }

  return (
    <>
      <h2 className={styles['header-title']}>Informations bancaires</h2>
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

        <ButtonLink
          link={{
            to: '', // TODO: le liens manque
            isExternal: true,
            target: '_blank',
          }}
          icon={fullLinkIcon}
          className={styles['information-link-button']}
        >
          En savoir plus
        </ButtonLink>
      </div>
      {selectedOffererBankAccounts &&
        selectedOffererBankAccounts?.bankAccounts.length > 0 && (
          <div className={styles['bank-accounts']}>
            {selectedOffererBankAccounts?.bankAccounts.map((bankAccount) => (
              <ReimbursementBankAccount
                bankAccount={bankAccount}
                offererId={selectedOfferer?.id}
                key={bankAccount.id}
                onUpdateButtonClick={(bankAccountId) => {
                  setSelectedBankAccount(
                    selectedOffererBankAccounts?.bankAccounts.find(
                      (bankAccount) => bankAccount.id === bankAccountId
                    ) ?? null
                  )
                }}
                managedVenues={selectedOffererBankAccounts.managedVenues}
                hasWarning={
                  (selectedOfferer &&
                    selectedOfferer?.venuesWithNonFreeOffersWithoutBankAccounts
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
          (selectedOfferer?.hasPendingBankAccount ||
            selectedOfferer?.hasValidBankAccount)
            ? ButtonVariant.SECONDARY
            : ButtonVariant.PRIMARY
        }
        onClick={() => {
          setShowAddBankInformationsDialog(true)
          logEvent?.(BankAccountEvents.CLICKED_ADD_BANK_ACCOUNT, {
            from: location.pathname,
            offererId: selectedOfferer?.id,
          })
        }}
      >
        Ajouter un compte bancaire
      </Button>
      {showAddBankInformationsDialog && (
        <AddBankInformationsDialog
          closeDialog={() => {
            setShowAddBankInformationsDialog(false)
          }}
          offererId={selectedOfferer?.id}
        />
      )}
      {selectedBankAccount !== null &&
        selectedOfferer !== null &&
        bankAccountVenues && (
          <LinkVenuesDialog
            offererId={selectedOfferer.id}
            selectedBankAccount={selectedBankAccount}
            managedVenues={bankAccountVenues}
            updateBankAccountVenuePricingPoint={
              updateBankAccountVenuePricingPoint
            }
            closeDialog={closeDialog}
          />
        )}
    </>
  )
}

export default BankInformations
