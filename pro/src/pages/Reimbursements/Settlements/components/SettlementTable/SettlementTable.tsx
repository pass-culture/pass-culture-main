import cn from 'classnames'
import { format } from 'date-fns'
import { useState } from 'react'

import {
  SettlementDisplayedStatus,
  type SettlementListResponseModel,
  type SettlementResponseModel,
} from '@/apiClient/v1'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import {
  TABLET_MEDIA_QUERY,
  useMediaQuery,
} from '@/commons/hooks/useMediaQuery'
import { ensureSelectedAdminOfferer } from '@/commons/store/user/selectors'
import {
  convertEuroToPacificFranc,
  formatPacificFranc,
} from '@/commons/utils/convertEuroToPacificFranc'
import { FORMAT_DD_MM_YYYY } from '@/commons/utils/date'
import { formatPrice } from '@/commons/utils/formatPrice'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import { Tag } from '@/design-system/Tag/Tag'
import fullDownIcon from '@/icons/full-down.svg'
import fullNextIcon from '@/icons/full-next.svg'
import strokeInstitutionIcon from '@/icons/stroke-institution.svg'
import strokeRepaymentIcon from '@/icons/stroke-repayment.svg'
import { type Column, Table, TableVariant } from '@/ui-kit/Table/Table'
import { Tooltip } from '@/ui-kit/Tooltip/Tooltip'

import { SettlementRowInvoicesModal } from '../SettlementRowInvoicesModal/SettlementRowInvoicesModal'
import { SettlementRowInvoicesTable } from '../SettlementRowInvoicesTable/SettlementRowInvoicesTable'
import { SETTLEMENT_STATUS_LABELS } from './constants'
import styles from './SettlementTable.module.scss'

type SettlementTableProps = {
  settlements: SettlementListResponseModel
  isLoading: boolean
  hasSettlement: boolean
  hasBankAccount: boolean
  onFilterReset: () => void
}

export type ExtendedSettlementResponseModel = SettlementResponseModel & {
  id: number
  isCaledonian: boolean
  invoicesCount: number
}

function getEmptyStateMessage(hasBankAccount: boolean) {
  if (!hasBankAccount) {
    return {
      icon: strokeInstitutionIcon,
      title: 'Aucun compte bancaire rattaché',
      subtitle:
        "Vos virements ne pourront pas être traités tant qu'aucun compte bancaire n'est actif. Rattachez-en un pour débloquer vos remboursements.",
      cta: (
        <Button
          as="router-link"
          to="/administration/remboursements/informations-bancaires"
          label="Rattacher un compte bancaire"
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.NEUTRAL}
          icon={fullNextIcon}
          iconPosition={IconPositionEnum.RIGHT}
        />
      ),
    }
  }
  return {
    icon: strokeRepaymentIcon,
    title: 'Aucun virement pour le moment',
    subtitle:
      "Ici, vous retrouverez vos virements une fois qu'ils sont émis. En attendant, vous pouvez consulter vos justificatifs.",
    cta: (
      <Button
        as="router-link"
        to="/administration/remboursements/justificatifs"
        label="Voir mes justificatifs"
        variant={ButtonVariant.TERTIARY}
        color={ButtonColor.NEUTRAL}
        icon={fullNextIcon}
        iconPosition={IconPositionEnum.RIGHT}
      />
    ),
  }
}

const getSettlementDateLabel = (settlement: ExtendedSettlementResponseModel) =>
  settlement.date ? format(new Date(settlement.date), FORMAT_DD_MM_YYYY) : '-'

const getResolvedByLabel = (settlement: ExtendedSettlementResponseModel) =>
  settlement.resolvedBy.length > 0
    ? `Voir ${settlement.resolvedBy.join(', ')}`
    : null

export const SettlementTable = ({
  settlements,
  isLoading,
  hasSettlement,
  hasBankAccount,
  onFilterReset,
}: SettlementTableProps): JSX.Element => {
  const selectedAdminOfferer = useAppSelector(ensureSelectedAdminOfferer)
  const isTabletOrSmaller = useMediaQuery(TABLET_MEDIA_QUERY)
  const [rowInvoicesToDisplay, setRowInvoicesToDisplay] =
    useState<ExtendedSettlementResponseModel | null>(null)

  function toggleRowToDisplay(row: ExtendedSettlementResponseModel) {
    setRowInvoicesToDisplay((currentDisplayedRow) =>
      currentDisplayedRow?.id === row.id ? null : row
    )
  }

  const columns: Column<ExtendedSettlementResponseModel>[] = [
    {
      id: 'label',
      label: 'N° de virement',
      sortable: true,
      ordererField: 'label',
      render: (settlement) => (
        <p className={styles['cell-label']}>{settlement.label}</p>
      ),
    },
    {
      id: 'date',
      label: "Date d'émission",
      sortable: true,
      ordererField: 'date',
      render: (settlement) => (
        <p className={styles['cell-date']}>
          {getSettlementDateLabel(settlement)}
        </p>
      ),
    },
    {
      id: 'bankAccount',
      label: 'Compte bancaire',
      sortable: true,
      ordererField: 'bankAccount',
      render: (settlement) => (
        <Tooltip content={settlement.bankAccount}>
          <p className={styles['cell-bank-account']}>
            {settlement.bankAccount}
          </p>
        </Tooltip>
      ),
    },
    {
      id: 'status',
      label: 'Statut',
      sortable: true,
      ordererField: 'status',
      render: (settlement) => {
        const { label, variant } = SETTLEMENT_STATUS_LABELS[settlement.status]
        return (
          <div className={styles['cell-status']}>
            <Tag label={label} variant={variant} />
          </div>
        )
      },
    },
    {
      id: 'amount',
      label: 'Montant',
      sortable: true,
      ordererField: 'amount',
      render: (settlement: ExtendedSettlementResponseModel) => (
        <p className={styles['cell-amount']}>
          {settlement.isCaledonian
            ? formatPacificFranc(convertEuroToPacificFranc(settlement.amount))
            : formatPrice(settlement.amount)}
        </p>
      ),
    },
    {
      id: 'invoicesCount',
      label: 'Justificatifs',
      sortable: true,
      ordererField: 'invoicesCount',
      render: (settlement) =>
        settlement.status === SettlementDisplayedStatus.EXECUTED &&
        settlement.invoicesCount,
    },
    {
      id: 'actions',
      label: 'Actions',
      render: (settlement) => (
        <div className={styles['cell-actions']}>
          {
            // EXECUTED -> display a button to show the invoices
            settlement.status === SettlementDisplayedStatus.EXECUTED &&
              settlement.invoicesCount > 0 && (
                <Button
                  label="Voir plus"
                  variant={ButtonVariant.TERTIARY}
                  size={ButtonSize.SMALL}
                  color={ButtonColor.NEUTRAL}
                  iconPosition={IconPositionEnum.RIGHT}
                  icon={fullDownIcon}
                  onClick={() => toggleRowToDisplay(settlement)}
                />
              )
          }

          {
            // REJECTED -> link to the bank accounts tab
            settlement.status === SettlementDisplayedStatus.REJECTED && (
              <Button
                as="router-link"
                variant={ButtonVariant.PRIMARY}
                to="/administration/remboursements/informations-bancaires"
                label="Remplacer le compte"
                size={ButtonSize.SMALL}
              />
            )
          }

          {
            // REJECTED_PROCESSED -> link to the bank accounts tab
            settlement.status ===
              SettlementDisplayedStatus.REJECTED_PROCESSED && (
              <p className={styles['cell-rejected']}>
                En attente de réémission
              </p>
            )
          }

          {
            // REJECTED_SOLVED -> link to the bank accounts tab
            settlement.status === SettlementDisplayedStatus.REJECTED_SOLVED && (
              <p className={styles['cell-rejected']}>
                {getResolvedByLabel(settlement)}
              </p>
            )
          }
        </div>
      ),
      header: (
        <p className={cn(styles['cell-header'], styles['cell-actions'])}>
          Actions
        </p>
      ),
    },
  ]

  const getInvoiceTable = (row: SettlementResponseModel) => {
    if (rowInvoicesToDisplay?.id !== row.id || isTabletOrSmaller) {
      return null
    }
    return {
      content: (
        <SettlementRowInvoicesTable
          invoices={rowInvoicesToDisplay?.invoices || []}
        />
      ),
      headerId: 'actions',
      rawDisplay: true,
    }
  }

  return (
    <>
      <Table
        title="Virements"
        columns={columns}
        data={settlements.map((s) => ({
          ...s,
          isCaledonian: selectedAdminOfferer.isCaledonian,
          invoicesCount: s.invoices.length,
        }))}
        selectable={true}
        getRowSelectionDateTime={getSettlementDateLabel}
        isLoading={isLoading}
        variant={TableVariant.COLLAPSE}
        noResult={{
          message: 'Aucun virement ne correspond à votre recherche',
          subtitle: 'Essayez de modifier vos critères de recherche.',
          resetMessage: 'Réinitialiser les filtres',
          onFilterReset,
        }}
        noData={{
          hasNoData: !hasSettlement,
          message: getEmptyStateMessage(hasBankAccount),
        }}
        getFullRow={getInvoiceTable}
      />
      {isTabletOrSmaller && (
        <SettlementRowInvoicesModal
          isOpen={!!rowInvoicesToDisplay?.id}
          onClose={() => setRowInvoicesToDisplay(null)}
          settlementRow={rowInvoicesToDisplay}
        />
      )}
    </>
  )
}
