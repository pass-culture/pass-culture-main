import React, { useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import { GetOffererBankAccountsResponseModel } from 'apiClient/v1'
import { useReimbursementContext } from 'context/ReimbursementContext/ReimbursementContext'
import fullLinkIcon from 'icons/full-link.svg'
import fullMoreIcon from 'icons/full-more.svg'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Spinner from 'ui-kit/Spinner/Spinner'

import styles from './BankInformations.module.scss'

const BankInformations = (): JSX.Element => {
  const { selectedOfferer } = useReimbursementContext()

  const [isOffererBankAccountsLoading, setIsOffererBankAccountsLoading] =
    useState<boolean>(false)
  const [, setSelectedOffererBankAccounts] =
    useState<GetOffererBankAccountsResponseModel | null>(null)

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
        setIsOffererBankAccountsLoading(false)
      }
    }

    if (selectedOfferer !== null) {
      getSelectedOffererBankAccounts(selectedOfferer.id)
    }
  }, [selectedOfferer])

  if (isOffererBankAccountsLoading) {
    return <Spinner className={styles['spinner']} />
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
            to: '',
            isExternal: true,
          }}
          icon={fullLinkIcon}
          className={styles['information-link-button']}
        >
          En savoir plus
        </ButtonLink>
      </div>
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
