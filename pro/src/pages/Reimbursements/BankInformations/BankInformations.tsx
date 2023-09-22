import React, { useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import {
  GetOffererBankAccountsResponseModel,
  GetOffererNameResponseModel,
} from 'apiClient/v1'
import fullLinkIcon from 'icons/full-link.svg'
import fullMoreIcon from 'icons/full-more.svg'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Spinner from 'ui-kit/Spinner/Spinner'

import styles from './BankInformations.module.scss'

const BankInformations = (): JSX.Element => {
  const [isOfferersLoading, setIsOfferersLoading] = useState<boolean>(false)
  const [isOffererBankAccountsLoading, setIsOffererBankAccountsLoading] =
    useState<boolean>(false)
  const [offerers, setOfferers] =
    useState<Array<GetOffererNameResponseModel> | null>(null)
  const [selectedOfferer, setSelectedOfferer] =
    useState<GetOffererBankAccountsResponseModel | null>(null)
  const [selectedOffererId, setSelectedOffererId] = useState<number | null>(
    null
  )

  useEffect(() => {
    const fetchData = async () => {
      setIsOfferersLoading(true)
      try {
        const { offerersNames } = await api.listOfferersNames()
        if (offerersNames) {
          setOfferers(offerersNames)
          setSelectedOffererId(offerersNames[0].id)
        }
        setIsOfferersLoading(false)
      } catch (error) {
        setIsOfferersLoading(false)
      }
    }
    fetchData()
  }, [])

  useEffect(() => {
    const getSelectedOffererBankAccounts = async (
      selectedOffererId: number
    ) => {
      setIsOffererBankAccountsLoading(true)
      try {
        const offererBankAccounts =
          await api.getOffererBankAccountsAndAttachedVenues(selectedOffererId)
        setSelectedOfferer(offererBankAccounts)
        setIsOffererBankAccountsLoading(false)
      } catch (error) {
        setIsOffererBankAccountsLoading(false)
      }
    }
    if (selectedOffererId !== null) {
      getSelectedOffererBankAccounts(selectedOffererId)
    }
  }, [selectedOffererId])

  const venuesWithNonFreeOffersNotLinkedToBankAccount = []
  const hasValidBankAccount = false
  const hasPendingBankAccount = false

  if (isOffererBankAccountsLoading || isOfferersLoading) {
    return <Spinner className={styles['spinner']} />
  }

  return (
    <>
      <div className="header">
        <h2 className="header-title">Informations bancaires</h2>
      </div>
      <div className={styles['information']}>
        {!hasValidBankAccount &&
          'Ajoutez au moins un compte bancaire pour percevoir vos remboursements.'}

        {hasValidBankAccount &&
          hasPendingBankAccount &&
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
          venuesWithNonFreeOffersNotLinkedToBankAccount.length > 0
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
