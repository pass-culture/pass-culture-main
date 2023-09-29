import React, { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'

import { api } from 'apiClient/api'
import { GetOffererBankAccountsResponseModel } from 'apiClient/v1'
import ReimbursementBankAccount from 'components/ReimbursementBankAccount/ReimbursementBankAccount'
import { useReimbursementContext } from 'context/ReimbursementContext/ReimbursementContext'
import { SelectOption } from 'custom_types/form'
import useNotification from 'hooks/useNotification'
import fullLinkIcon from 'icons/full-link.svg'
import fullMoreIcon from 'icons/full-more.svg'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import SelectInput from 'ui-kit/form/Select/SelectInput'
import Spinner from 'ui-kit/Spinner/Spinner'
import { sortByLabel } from 'utils/strings'

import styles from './BankInformations.module.scss'

const BankInformations = (): JSX.Element => {
  const notify = useNotification()

  const { offerers, selectedOfferer, setSelectedOfferer } =
    useReimbursementContext()

  const [isOffererBankAccountsLoading, setIsOffererBankAccountsLoading] =
    useState<boolean>(false)
  // TODO: use bank accounts
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [selectedOffererBankAccounts, setSelectedOffererBankAccounts] =
    useState<GetOffererBankAccountsResponseModel | null>(null)
  const [searchParams, setSearchParams] = useSearchParams()
  const [isOffererLoading, setIsOffererLoading] = useState<boolean>(false)

  const { structure: offererId } = Object.fromEntries(searchParams)
  const [offererOptions, setOffererOptions] = useState<SelectOption[]>([])

  const updateOfferer = async (newOffererId: string) => {
    if (newOffererId !== '') {
      setIsOffererLoading(true)
      const offerer = await api.getOfferer(Number(newOffererId))
      setSelectedOfferer(offerer)
      setIsOffererLoading(false)
    }
  }

  useEffect(() => {
    if (offererId && offerers && offerers?.length > 0) {
      updateOfferer(offererId)
    }
    if (searchParams.has('structure')) {
      searchParams.delete('structure')
      setSearchParams(searchParams)
    }
  }, [])

  const selectedOffererId = selectedOfferer?.id.toString() ?? ''

  useEffect(() => {
    if (offerers && offerers.length > 1) {
      const initialOffererOptions = sortByLabel(
        offerers.map(item => ({
          value: item['id'].toString(),
          label: item['name'],
        }))
      )
      setOffererOptions(initialOffererOptions)
    }
  }, [offerers])

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

    selectedOfferer && getSelectedOffererBankAccounts(selectedOfferer.id)
  }, [selectedOfferer])

  if (isOffererBankAccountsLoading || isOffererLoading) {
    return <Spinner />
  }

  return (
    <>
      <div className="header">
        <h2 className="header-title">Informations bancaires</h2>
      </div>
      <div className={styles['information']}>
        {!selectedOfferer?.hasValidBankAccount &&
          !selectedOfferer?.hasPendingBankAccount &&
          'Ajoutez au moins un compte bancaire pour percevoir vos remboursements.'}

        {(selectedOfferer?.hasValidBankAccount ||
          selectedOfferer?.hasPendingBankAccount) &&
          "Vous pouvez ajouter plusieurs comptes bancaires afin de percevoir les remboursements de vos offres. Chaque compte bancaire fera l'objet d'un remboursement et d'un justificatif de remboursement distincts."}

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
              onChange={e => updateOfferer(e.target.value)}
              data-testid="select-input-offerer"
              name="offererId"
              options={offererOptions}
              value={selectedOfferer?.id.toString() ?? ''}
            />
          </div>
        </div>
      )}
      <div className={styles['bank-accounts']}>
        {selectedOffererBankAccounts?.bankAccounts.map(bankAccount => (
          <ReimbursementBankAccount
            bankAccount={bankAccount}
            venuesWithNonFreeOffersNotLinkedToBankAccount={
              selectedOfferer?.venuesWithNonFreeOffersWithoutBankAccounts ?? []
            }
            bankAccountsNumber={
              selectedOffererBankAccounts?.bankAccounts.length
            }
            key={bankAccount.id}
          />
        ))}
      </div>
      <Button
        icon={fullMoreIcon}
        className={styles['add-bank-account-button']}
        variant={
          /* istanbul ignore next : graphic changes */ selectedOfferer &&
          selectedOfferer?.venuesWithNonFreeOffersWithoutBankAccounts.length > 0
            ? ButtonVariant.SECONDARY
            : ButtonVariant.PRIMARY
        }
      >
        Ajouter un compte bancaire
      </Button>
      {offerers && offerers.length > 1 && (
        <div className={styles['select-offerer-section']}>
          <div className={styles['select-offerer-input']}>
            <div className={styles['select-offerer-input-label']}>
              <label htmlFor="selected-offerer">Structure</label>
            </div>
            <SelectInput
              onChange={e => updateOfferer(e.target.value)}
              id="selected-offerer"
              data-testid="select-input-offerer"
              name="offererId"
              options={offererOptions}
              value={selectedOffererId}
            />
          </div>
        </div>
      )}
      <Button
        icon={fullMoreIcon}
        className={styles['add-bank-account-button']}
        variant={
          selectedOfferer &&
          selectedOfferer?.venuesWithNonFreeOffersWithoutBankAccounts.length > 0
            ? ButtonVariant.SECONDARY
            : ButtonVariant.PRIMARY
        }
      >
        Ajouter un compte bancaire
      </Button>
    </>
  )
}

export default BankInformations
