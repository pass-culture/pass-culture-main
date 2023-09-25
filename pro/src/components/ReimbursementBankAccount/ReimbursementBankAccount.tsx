import React from 'react'

import { BankAccountResponseModel } from 'apiClient/v1'
import fullLinkIcon from 'icons/full-link.svg'
import fullWaitIcon from 'icons/full-wait.svg'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './ReimbursementBankAccount.module.scss'

const ReimbursementBankAccount = ({
  bankAccount,
}: {
  bankAccount: BankAccountResponseModel
}): JSX.Element => {
  return (
    <div className={styles['bank-account']}>
      <div className={styles['informations-section']}>
        <div className={styles['informations-section-title']}>
          {bankAccount.label}
        </div>
        <div className={styles['informations-section-content']}>
          <div>IBAN: {bankAccount.obfuscatedIban}</div>
          <div>BIC: {bankAccount.bic}</div>
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
            {/*TODO: add icon depending linked venues */}
          </div>
          <div className={styles['linked-venues-content']}>
            {bankAccount.isActive && bankAccount.linkedVenues.length === 0 && (
              <div className={styles['issue-text']}>
                Aucun lieu n'est rattaché à ce compte bancaire.
                {/* TODO: message when no linked and all venues already linked*/}
              </div>
            )}
            {
              // TODO: 1 or more venues associated are not linked
              // <div className={styles['issue-text']}>
              //   Un de vos lieux n'est pas rattaché.
              // </div>
            }
            {bankAccount.isActive && bankAccount.linkedVenues.length > 0 && (
              <>
                <div className={styles['linked-venues']}>
                  {bankAccount.linkedVenues.map(venue => (
                    <div className={styles['linked-venue']}>
                      {venue.commonName}
                    </div>
                  ))}
                </div>
                <Button variant={ButtonVariant.SECONDARY}>Modifier</Button>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default ReimbursementBankAccount
