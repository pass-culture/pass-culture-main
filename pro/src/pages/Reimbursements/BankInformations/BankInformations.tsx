import React, { useEffect, useState } from 'react'
import { useLocation, useSearchParams } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  BankAccountResponseModel,
  GetOffererBankAccountsResponseModel,
} from 'apiClient/v1'
import ConfirmDialog from 'components/Dialog/ConfirmDialog'
import ReimbursementBankAccount from 'components/ReimbursementBankAccount/ReimbursementBankAccount'
import { useReimbursementContext } from 'context/ReimbursementContext/ReimbursementContext'
import { BankAccountEvents } from 'core/FirebaseEvents/constants'
import { SelectOption } from 'custom_types/form'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import fullLinkIcon from 'icons/full-link.svg'
import fullMoreIcon from 'icons/full-more.svg'
import strokeWarningIcon from 'icons/stroke-warning.svg'
import LinkVenuesDialog from 'pages/Reimbursements/BankInformations/LinkVenuesDialog'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import SelectInput from 'ui-kit/form/Select/SelectInput'
import Spinner from 'ui-kit/Spinner/Spinner'
import { sortByLabel } from 'utils/strings'

import AddBankInformationsDialog from './AddBankInformationsDialog'
import styles from './BankInformations.module.scss'

const BankInformations = (): JSX.Element => {
  const notify = useNotification()
  const { logEvent } = useAnalytics()
  const location = useLocation()

  const [showAddBankInformationsDialog, setShowAddBankInformationsDialog] =
    useState(false)
  const { offerers, selectedOfferer, setSelectedOfferer } =
    useReimbursementContext()

  const [isOffererBankAccountsLoading, setIsOffererBankAccountsLoading] =
    useState<boolean>(false)
  const [selectedOffererBankAccounts, setSelectedOffererBankAccounts] =
    useState<GetOffererBankAccountsResponseModel | null>(null)
  const [searchParams, setSearchParams] = useSearchParams()
  const [isOffererLoading, setIsOffererLoading] = useState<boolean>(false)
  const [showDiscadChangesDialog, setShowDiscardChangesDialog] =
    useState<boolean>(false)

  const [selectedBankAccount, setSelectedBankAccount] =
    useState<BankAccountResponseModel | null>(null)
  const { structure: offererId } = Object.fromEntries(searchParams)

  const offererOptions: SelectOption[] =
    offerers && offerers.length > 1
      ? sortByLabel(
          offerers.map((item) => ({
            value: item['id'].toString(),
            label: item['name'],
          }))
        )
      : []

  const updateOfferer = async (newOffererId: string) => {
    if (newOffererId !== '') {
      setIsOffererLoading(true)
      const offerer = await api.getOfferer(Number(newOffererId))
      setSelectedOfferer(offerer)
      setIsOffererLoading(false)
    }
  }

  useEffect(() => {
    if (!offerers || offerers.length === 0) {
      return
    }

    if (offererId) {
      void updateOfferer(offererId)
    }
    if (searchParams.has('structure')) {
      searchParams.delete('structure')
      setSearchParams(searchParams)
    }
  }, [])

  useEffect(() => {
    const getSelectedOffererBankAccounts = async (
      selectedOffererId: number
    ) => {
      setIsOffererBankAccountsLoading(true)
      try {
        const offererBankAccounts =
          await api.getOffererBankAccountsAndAttachedVenues(selectedOffererId)
        setSelectedOffererBankAccounts(offererBankAccounts)
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
  }, [selectedOfferer])

  if (isOffererBankAccountsLoading || isOffererLoading) {
    return <Spinner />
  }

  return (
    <>
      <h2 className="header-title">Informations bancaires</h2>
      <div className={styles['information']}>
        {!selectedOfferer?.hasValidBankAccount &&
          !selectedOfferer?.hasPendingBankAccount &&
          'Ajoutez au moins un compte bancaire pour percevoir vos remboursements.'}

        {(selectedOfferer?.hasValidBankAccount ||
          selectedOfferer?.hasPendingBankAccount) && (
          <>
            Vous pouvez ajouter plusieurs comptes bancaires afin de percevoir
            les remboursements de vos offres. Chaque compte bancaire fera
            l'objet d'un remboursement et d'un justificatif de remboursement
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
      {offerers && offerers.length > 1 && (
        <div className={styles['select-offerer-section']}>
          <div className={styles['select-offerer-input']}>
            <div className={styles['select-offerer-input-label']}>
              <label htmlFor="selected-offerer">Structure</label>
            </div>
            <SelectInput
              onChange={(e) => updateOfferer(e.target.value)}
              data-testid="select-input-offerer"
              name="offererId"
              options={offererOptions}
              value={selectedOfferer?.id.toString() ?? ''}
            />
          </div>
        </div>
      )}
      {selectedOffererBankAccounts &&
        selectedOffererBankAccounts?.bankAccounts.length > 0 && (
          <div className={styles['bank-accounts']}>
            {selectedOffererBankAccounts?.bankAccounts.map((bankAccount) => (
              <ReimbursementBankAccount
                bankAccount={bankAccount}
                venuesNotLinkedLength={
                  selectedOfferer?.venuesWithNonFreeOffersWithoutBankAccounts
                    .length ?? 0
                }
                bankAccountsNumber={
                  selectedOffererBankAccounts?.bankAccounts.length
                }
                offererId={selectedOfferer?.id}
                key={bankAccount.id}
                onUpdateButtonClick={(bankAccountId) => {
                  setSelectedBankAccount(
                    selectedOffererBankAccounts?.bankAccounts.find(
                      (bankAccount) => bankAccount.id === bankAccountId
                    ) ?? null
                  )
                }}
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
      {selectedBankAccount !== null && selectedOfferer !== null && (
        <LinkVenuesDialog
          offererId={selectedOfferer.id}
          selectedBankAccount={selectedBankAccount}
          managedVenues={selectedOffererBankAccounts?.managedVenues}
          closeDialog={(update?: boolean) => {
            if (update) {
              // eslint-disable-next-line @typescript-eslint/no-floating-promises
              updateOfferer(selectedOfferer.id.toString())
            }
            setSelectedBankAccount(null)
          }}
          showConfirmDiscardChanges={() => {
            setShowDiscardChangesDialog(true)
          }}
        />
      )}
      {showDiscadChangesDialog && (
        <ConfirmDialog
          icon={strokeWarningIcon}
          onCancel={() => setShowDiscardChangesDialog(false)}
          title="Les informations non sauvegardées ne seront pas prises en compte"
          onConfirm={() => {
            setShowDiscardChangesDialog(false)
            setSelectedBankAccount(null)
          }}
          confirmText="Quitter sans enregistrer "
          cancelText="Annuler"
        />
      )}
    </>
  )
}

export default BankInformations
