import { useLocation } from 'react-router'

import {
  BankAccountApplicationStatus,
  type BankAccountResponseModel,
  type ManagedVenue,
} from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { BankAccountEvents } from '@/commons/core/FirebaseEvents/constants'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import fullErrorIcon from '@/icons/full-error.svg'
import fullLinkIcon from '@/icons/full-link.svg'
import fullWaitIcon from '@/icons/full-wait.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './ReimbursementBankAccount.module.scss'

interface ReimbursementBankAccountProps {
  bankAccount: BankAccountResponseModel
  managedVenues: ManagedVenue[]
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
  const { logEvent } = useAnalytics()
  const location = useLocation()
  const venuesNotLinkedToBankAccount = managedVenues.filter(
    (venue) => !venue.bankAccountId
  ).length

  const linkedCount = bankAccount.linkedVenues.length
  const hasManagedVenues = managedVenues.length > 0
  const hasLinkedVenues = linkedCount > 0
  const showWarningIcon = hasWarning && hasManagedVenues

  const showNoLinkedMessage = !hasLinkedVenues
  const showPartialWarning = hasLinkedVenues && venuesNotLinkedToBankAccount > 0

  const handleUpdateClick = () => {
    onUpdateButtonClick?.(bankAccount.id)
    logEvent(BankAccountEvents.CLICKED_CHANGE_VENUE_TO_BANK_ACCOUNT, {
      from: location.pathname,
      offererId,
    })
  }

  const handleAttachClick = () => {
    logEvent(BankAccountEvents.CLICKED_ADD_VENUE_TO_BANK_ACCOUNT, {
      from: location.pathname,
      offererId,
    })
    onUpdateButtonClick?.(bankAccount.id)
  }

  return (
    <div className={styles['bank-account']}>
      <div className={styles['informations-section']}>
        <div className={styles['informations-section-title']}>
          {bankAccount.label}
        </div>
        <div className={styles['informations-section-content']}>
          IBAN : **** {bankAccount.obfuscatedIban.slice(-4)}
        </div>
      </div>
      {bankAccount.status === BankAccountApplicationStatus.EN_CONSTRUCTION ||
      bankAccount.status === BankAccountApplicationStatus.EN_INSTRUCTION ||
      bankAccount.status === BankAccountApplicationStatus.A_CORRIGER ? (
        <div className={styles['linked-venues-section']}>
          <Banner
            title={
              'Statut du dossier : ' +
              `${
                bankAccount.status === BankAccountApplicationStatus.A_CORRIGER
                  ? 'informations manquantes'
                  : 'en cours de validation'
              }`
            }
            icon={
              bankAccount.status === BankAccountApplicationStatus.A_CORRIGER
                ? fullErrorIcon
                : fullWaitIcon
            }
            variant={
              bankAccount.status === BankAccountApplicationStatus.A_CORRIGER
                ? BannerVariants.ERROR
                : BannerVariants.DEFAULT
            }
            actions={[
              {
                href:
                  bankAccount.status === BankAccountApplicationStatus.A_CORRIGER
                    ? `https://demarche.numerique.gouv.fr/dossiers/${bankAccount.dsApplicationId}`
                    : `https://demarche.numerique.gouv.fr/dossiers/${bankAccount.dsApplicationId}/messagerie`,
                label:
                  bankAccount.status === BankAccountApplicationStatus.A_CORRIGER
                    ? 'Compléter le dossier'
                    : 'Voir le dossier',
                isExternal: true,
                type: 'link',
                icon: fullLinkIcon,
                iconAlt: 'Nouvelle fenêtre',
                onClick: () => {
                  logEvent(
                    BankAccountEvents.CLICKED_BANK_DETAILS_RECORD_FOLLOW_UP,
                    {
                      from: location.pathname,
                      offererId: offererId,
                    }
                  )
                },
              },
            ]}
          />
        </div>
      ) : (
        <div
          className={styles['linked-venues-section']}
          data-testid="reimbursement-bank-account-linked-venues"
        >
          <div className={styles['linked-venues-section-title']}>
            {pluralizeFr(
              linkedCount,
              'Structure rattachée',
              'Structures rattachées'
            )}{' '}
            à ce compte bancaire
            {showWarningIcon && (
              <SvgIcon
                src={fullErrorIcon}
                alt="Une action est requise"
                width="20"
                className={styles['error-icon']}
              />
            )}
          </div>

          {!hasManagedVenues && null}

          {hasManagedVenues && (
            <div className={styles['linked-venues-content']}>
              {showNoLinkedMessage && (
                <div className={styles['issue-text']}>
                  Aucune structure n’est rattachée à ce compte bancaire.
                  {venuesNotLinkedToBankAccount === 0 &&
                    ' Désélectionnez une structure déjà rattachée et rattachez-la à ce compte bancaire.'}
                </div>
              )}

              {showPartialWarning && (
                <div className={styles['issue-text']}>
                  Certaines de vos structures ne sont pas rattachées.
                </div>
              )}

              {hasLinkedVenues && (
                <>
                  <div className={styles['linked-venues']}>
                    {bankAccount.linkedVenues.map(({ id, commonName }) => (
                      <div className={styles['linked-venue']} key={id}>
                        {commonName}
                      </div>
                    ))}
                  </div>

                  <Button
                    variant={ButtonVariant.SECONDARY}
                    onClick={handleUpdateClick}
                    ref={updateButtonRef}
                    label="Modifier"
                  />
                </>
              )}

              {!hasLinkedVenues && venuesNotLinkedToBankAccount > 0 && (
                <Button
                  onClick={handleAttachClick}
                  ref={updateButtonRef}
                  label="Rattacher une structure"
                />
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
