import React from 'react'

import fullLinkIcon from 'icons/full-link.svg'
import fullMoreIcon from 'icons/full-more.svg'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './BankInformations.module.scss'

const BankInformations = (): JSX.Element => {
  // TODO: request api
  const venuesWithNonFreeOffersNotLinkedToBankAccount = []
  const hasValidBankAccount = false
  const hasPendingBankAccount = false

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
