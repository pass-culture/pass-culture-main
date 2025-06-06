import cn from 'classnames'
import { useLocation } from 'react-router'

import {
  BankAccountApplicationStatus,
  BankAccountResponseModel,
  ManagedVenues,
} from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { BankAccountEvents } from 'commons/core/FirebaseEvents/constants'
import { pluralizeString } from 'commons/utils/pluralize'
import fullErrorIcon from 'icons/full-error.svg'
import fullLinkIcon from 'icons/full-link.svg'
import fullWaitIcon from 'icons/full-wait.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './ReimbursementBankAccount.module.scss'

interface ReimbursementBankAccountProps {
  bankAccount: BankAccountResponseModel
  managedVenues: ManagedVenues[]
  onUpdateButtonClick?: (id: number) => void
  offererId?: number
  hasWarning?: boolean
  updateButtonRef?: React.RefObject<HTMLButtonElement>
}

export const ReimbursementBankAccount = ({
  bankAccount,
  onUpdateButtonClick,
  offererId,
  managedVenues,
  hasWarning = false,
  updateButtonRef,
}: ReimbursementBankAccountProps): JSX.Element => {
  const hasLinkedVenues = bankAccount.linkedVenues.length > 0
  const { logEvent } = useAnalytics()
  const location = useLocation()
  const venuesNotLinkedToBankAccount = managedVenues.filter(
    (venue) => !venue.bankAccountId
  ).length

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
      bankAccount.status === BankAccountApplicationStatus.EN_INSTRUCTION ||
      bankAccount.status === BankAccountApplicationStatus.A_CORRIGER ? (
        <div
          className={cn(styles['pending-account'], {
            [styles['needs-correction']]:
              bankAccount.status === BankAccountApplicationStatus.A_CORRIGER,
          })}
        >
          <SvgIcon
            src={
              bankAccount.status === BankAccountApplicationStatus.A_CORRIGER
                ? fullErrorIcon
                : fullWaitIcon
            }
            alt={''}
            width="48"
            className={cn(styles['status-icon'], {
              [styles['error-icon']]:
                bankAccount.status === BankAccountApplicationStatus.A_CORRIGER,
            })}
          />
          <div>
            Statut du dossier :{' '}
            <span className={styles['account-status']}>
              {bankAccount.status === BankAccountApplicationStatus.A_CORRIGER
                ? 'informations manquantes'
                : 'en cours de validation'}
            </span>
          </div>
          <ButtonLink
            to={
              bankAccount.status === BankAccountApplicationStatus.A_CORRIGER
                ? `https://www.demarches-simplifiees.fr/dossiers/${bankAccount.dsApplicationId}`
                : `https://www.demarches-simplifiees.fr/dossiers/${bankAccount.dsApplicationId}/messagerie`
            }
            isExternal
            aria-label="Nouvelle fenêtre"
            opensInNewTab
            onClick={() => {
              logEvent(
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
            {bankAccount.status === BankAccountApplicationStatus.A_CORRIGER
              ? 'Compléter le dossier'
              : 'Voir le dossier'}
          </ButtonLink>
        </div>
      ) : (
        <div
          className={styles['linked-venues-section']}
          data-testid="reimbursement-bank-account-linked-venues"
        >
          <div className={styles['linked-venues-section-title']}>
            {pluralizeString(
              'Structure rattachée',
              bankAccount.linkedVenues.length
            )}{' '}
            à ce compte bancaire
            {hasWarning && managedVenues.length > 0 && (
              <SvgIcon
                src={fullErrorIcon}
                alt="Une action est requise"
                width="20"
                className={styles['error-icon']}
              />
            )}
          </div>
          {managedVenues.length > 0 && (
            <div className={styles['linked-venues-content']}>
              {!hasLinkedVenues && (
                <div className={styles['issue-text']}>
                  Aucune structure n’est rattachée à ce compte bancaire
                  {'. '}
                  {venuesNotLinkedToBankAccount === 0 &&
                    'Désélectionnez une structure déjà rattachée et rattachez-la à ce compte bancaire.'}
                </div>
              )}
              {hasLinkedVenues && venuesNotLinkedToBankAccount > 0 && (
                <div className={styles['issue-text']}>
                  Certaines de vos structures ne sont pas rattachées.
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
                      logEvent(
                        BankAccountEvents.CLICKED_CHANGE_VENUE_TO_BANK_ACCOUNT,
                        {
                          from: location.pathname,
                          offererId,
                        }
                      )
                    }}
                    ref={updateButtonRef}
                  >
                    Modifier
                  </Button>
                </>
              )}
              {!hasLinkedVenues && venuesNotLinkedToBankAccount > 0 && (
                <Button
                  onClick={() => {
                    logEvent(
                      BankAccountEvents.CLICKED_ADD_VENUE_TO_BANK_ACCOUNT,
                      {
                        from: location.pathname,
                        offererId,
                      }
                    )
                    onUpdateButtonClick?.(bankAccount.id)
                  }}
                  ref={updateButtonRef}
                >
                  Rattacher une structure
                </Button>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
