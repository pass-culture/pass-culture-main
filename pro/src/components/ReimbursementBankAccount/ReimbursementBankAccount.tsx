import React from 'react'

import { BankAccountResponseModel } from 'apiClient/v1'
import fullErrorIcon from 'icons/full-error.svg'
import fullLinkIcon from 'icons/full-link.svg'
import fullWaitIcon from 'icons/full-wait.svg'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './ReimbursementBankAccount.module.scss'

interface ReimbursementBankAccountProps {
  bankAccount: BankAccountResponseModel
  venuesWithNonFreeOffersNotLinkedToBankAccount: number[]
  bankAccountsNumber: number
}

const ReimbursementBankAccount = ({
  bankAccount,
  venuesWithNonFreeOffersNotLinkedToBankAccount,
  bankAccountsNumber,
}: ReimbursementBankAccountProps): JSX.Element => {
  return (
    <div className={styles['bank-account']}>
      <div className={styles['informations-section']}>
        <div className={styles['informations-section-title']}>
          {bankAccount.label}
        </div>
        <div className={styles['informations-section-content']}>
          <div>IBAN : **** {bankAccount.obfuscatedIban.slice(-4)}</div>
          <div>BIC : {bankAccount.bic}</div>
        </div>
      </div>
      {!bankAccount.isActive && (
        <div className={styles['pending-account']}>
          <SvgIcon
            src={fullWaitIcon}
            alt={''}
            width="48"
            className={styles['wait-icon']}
          />
          <div>Compte bancaire en cours de validation par nos services</div>
          <ButtonLink
            link={{
              to: '',
              isExternal: true,
            }}
            icon={fullLinkIcon}
            className={styles['ds-link-button']}
          >
            Suivre le dossier
          </ButtonLink>
        </div>
      )}
      {bankAccount.isActive && (
        <div className={styles['linked-venues-section']}>
          <div className={styles['linked-venues-section-title']}>
            Lieu(x) rattaché(s) à ce compte bancaire
            {bankAccount.linkedVenues.length === 0 && (
              <SvgIcon
                src={fullErrorIcon}
                alt="Une action est requise"
                width="20"
                className={styles['error-icon']}
              />
            )}
          </div>
          <div className={styles['linked-venues-content']}>
            {bankAccount.linkedVenues.length === 0 && (
              <div className={styles['issue-text']}>
                Aucun lieu n'est rattaché à ce compte bancaire.
                {venuesWithNonFreeOffersNotLinkedToBankAccount.length === 0 &&
                  bankAccountsNumber > 1 &&
                  ' Désélectionnez un lieu déjà rattaché et rattachez-le à ce compte bancaire.'}
              </div>
            )}
            {bankAccount.linkedVenues.length > 0 &&
              venuesWithNonFreeOffersNotLinkedToBankAccount.length > 0 && (
                <div className={styles['issue-text']}>
                  {venuesWithNonFreeOffersNotLinkedToBankAccount.length > 1
                    ? 'Certains de vos lieux ne sont pas rattachés'
                    : "Un de vos lieux n'est pas rattaché."}
                </div>
              )}
            {bankAccount.linkedVenues.length > 0 && (
              <>
                <div className={styles['linked-venues']}>
                  {bankAccount.linkedVenues.map(venue => (
                    <div className={styles['linked-venue']} key={venue.id}>
                      {venue.commonName}
                    </div>
                  ))}
                </div>
                {bankAccount.linkedVenues.length > 0 ? (
                  <Button variant={ButtonVariant.SECONDARY}>Modifier</Button>
                ) : (
                  <Button>Rattacher</Button>
                )}
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default ReimbursementBankAccount
