import React from 'react'
import { useLocation } from 'react-router-dom'

import {
  BankAccountApplicationStatus,
  BankAccountResponseModel,
} from 'apiClient/v1'
import { BankAccountEvents } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import fullErrorIcon from 'icons/full-error.svg'
import fullLinkIcon from 'icons/full-link.svg'
import fullWaitIcon from 'icons/full-wait.svg'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './ReimbursementBankAccount.module.scss'

interface ReimbursementBankAccountProps {
  bankAccount: BankAccountResponseModel
  venuesNotLinkedLength: number
  bankAccountsNumber: number
  onUpdateButtonClick?: (id: number) => void
  offererId?: number
}

const ReimbursementBankAccount = ({
  bankAccount,
  venuesNotLinkedLength,
  bankAccountsNumber,
  onUpdateButtonClick,
  offererId,
}: ReimbursementBankAccountProps): JSX.Element => {
  const hasLinkedVenues = bankAccount.linkedVenues.length > 0
  const { logEvent } = useAnalytics()
  const location = useLocation()

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
      {bankAccount.status === BankAccountApplicationStatus.EN_CONSTRUCTION ||
      bankAccount.status === BankAccountApplicationStatus.EN_INSTRUCTION ? (
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
              to: '', // TODO: change when link is available.
              isExternal: true,
            }}
            onClick={() => {
              logEvent?.(
                BankAccountEvents.CLICKED_BANK_DETAILS_RECORD_FOLLOW_UP,
                {
                  from: location.pathname,
                  offererId: offererId,
                }
              )
            }}
            icon={fullLinkIcon}
            className={styles['ds-link-button']}
          >
            Suivre le dossier
          </ButtonLink>
        </div>
      ) : (
        <div className={styles['linked-venues-section']}>
          <div className={styles['linked-venues-section-title']}>
            Lieu(x) rattaché(s) à ce compte bancaire
            {(!hasLinkedVenues ||
              (hasLinkedVenues && venuesNotLinkedLength > 0)) && (
              <SvgIcon
                src={fullErrorIcon}
                alt="Une action est requise"
                width="20"
                className={styles['error-icon']}
              />
            )}
          </div>
          <div className={styles['linked-venues-content']}>
            {!hasLinkedVenues && (
              <div className={styles['issue-text']}>
                Aucun lieu n’est rattaché à ce compte bancaire.
                {venuesNotLinkedLength === 0 &&
                  bankAccountsNumber > 1 &&
                  ' Désélectionnez un lieu déjà rattaché et rattachez-le à ce compte bancaire.'}
              </div>
            )}
            {hasLinkedVenues && venuesNotLinkedLength > 0 && (
              <div className={styles['issue-text']}>
                {venuesNotLinkedLength > 1
                  ? 'Certains de vos lieux ne sont pas rattachés'
                  : 'Un de vos lieux n’est pas rattaché.'}
              </div>
            )}
            {hasLinkedVenues && (
              <>
                <div className={styles['linked-venues']}>
                  {bankAccount.linkedVenues.map((venue) => (
                    <div className={styles['linked-venue']} key={venue.id}>
                      {venue.commonName}
                    </div>
                  ))}
                </div>
                <Button
                  variant={ButtonVariant.SECONDARY}
                  onClick={() => {
                    onUpdateButtonClick?.(bankAccount.id)
                    logEvent?.(
                      BankAccountEvents.CLICKED_CHANGE_VENUE_TO_BANK_ACCOUNT,
                      {
                        from: location.pathname,
                        offererId,
                      }
                    )
                  }}
                >
                  Modifier
                </Button>
              </>
            )}
            {!hasLinkedVenues && venuesNotLinkedLength > 0 && (
              <Button
                onClick={() => {
                  logEvent?.(
                    BankAccountEvents.CLICKED_ADD_VENUE_TO_BANK_ACCOUNT,
                    {
                      from: location.pathname,
                      offererId,
                    }
                  )
                  onUpdateButtonClick?.(bankAccount.id)
                }}
              >
                Rattacher un lieu
              </Button>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default ReimbursementBankAccount
