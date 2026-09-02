import cn from 'classnames'
import { format } from 'date-fns'

import type {
  SettlementListResponseModel,
  SettlementResponseModel,
} from '@/apiClient/v1'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedAdminOfferer } from '@/commons/store/user/selectors'
import {
  convertEuroToPacificFranc,
  formatPacificFranc,
} from '@/commons/utils/convertEuroToPacificFranc'
import { FORMAT_DD_MM_YYYY } from '@/commons/utils/date'
import { formatPrice } from '@/commons/utils/formatPrice'
import { noop } from '@/commons/utils/noop'
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

import { SETTLEMENT_STATUS_LABELS } from './constants'
import styles from './SettlementTable.module.scss'

type SettlementTableProps = {
  settlements: SettlementListResponseModel
  isLoading: boolean
  hasSettlement: boolean
  hasBankAccount: boolean
}

type ExtendedSettlementResponseModel = SettlementResponseModel & {
  id: number
  isCaledonian?: boolean
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

const columns: Column<ExtendedSettlementResponseModel>[] = [
  {
    id: 'label',
    label: 'N° de virement',
    sortable: true,
    ordererField: 'label',
    render: (settlement) => settlement.label,
  },
  {
    id: 'date',
    label: "Date d'émission",
    sortable: true,
    ordererField: 'date',
    render: (settlement) => getSettlementDateLabel(settlement),
  },
  {
    id: 'bankAccount',
    label: 'Compte bancaire',
    sortable: true,
    ordererField: 'bankAccount',
    render: (settlement) => (
      <p className={styles['cell-bank-account']}>{settlement.bankAccount}</p>
    ),
  },
  {
    id: 'status',
    label: 'Statut du virement',
    sortable: true,
    ordererField: 'status',
    render: (settlement) => {
      const { label, variant } = SETTLEMENT_STATUS_LABELS[settlement.status]
      return <Tag label={label} variant={variant} />
    },
  },
  {
    id: 'amount',
    label: 'Montant',
    sortable: true,
    ordererField: 'amount',
    render: (settlement: ExtendedSettlementResponseModel) => (
      <div
        className={cn({
          [styles['negative-amount']]: settlement.amount < 0,
          [styles['positive-amount']]: settlement.amount > 0,
        })}
      >
        {settlement.isCaledonian
          ? formatPacificFranc(convertEuroToPacificFranc(settlement.amount))
          : formatPrice(settlement.amount)}
      </div>
    ),
  },
  {
    id: 'invoicesCount',
    label: 'Nombre de justificatifs',
    sortable: true,
    ordererField: 'invoicesCount',
    render: (settlement) => settlement.invoicesCount,
  },
  {
    id: 'actions',
    label: 'Actions',
    render: () => (
      <div className={styles['cell-actions']}>
        <Button
          label="Voir plus"
          variant={ButtonVariant.TERTIARY}
          size={ButtonSize.SMALL}
          color={ButtonColor.NEUTRAL}
          iconPosition={IconPositionEnum.RIGHT}
          icon={fullDownIcon}
          disabled // TODO(mdesquilbet, 19/08/2026): to remove when creating the accordeon
        />
      </div>
    ),
    header: <div className={styles['cell-actions']}>Actions</div>,
  },
]

export const SettlementTable = ({
  settlements,
  isLoading,
  hasSettlement,
  hasBankAccount,
}: SettlementTableProps): JSX.Element => {
  const selectedAdminOfferer = useAppSelector(ensureSelectedAdminOfferer)
  // const [checkedSettlements, setCheckedSettlements] = useState<string[]>([])

  return (
    <div className={styles[`settlement-table`]}>
      <Table
        title="Virements"
        columns={columns}
        data={settlements.map((s) => ({
          ...s,
          isCaledonian: selectedAdminOfferer.isCaledonian,
        }))}
        selectable={true}
        getRowSelectionDateTime={getSettlementDateLabel}
        isLoading={isLoading}
        // onSelectionChange={(rows) => {
        //   setCheckedSettlements(rows.map((row) => row.id.toString()))
        // }}
        variant={TableVariant.COLLAPSE}
        noResult={{
          message: 'Aucun virement ne correspond à votre recherche',
          subtitle: 'Essayez de modifier vos critères de recherche.',
          resetMessage: 'Réinitialiser les filtres',
          onFilterReset: noop, // TODO(mdesquilbet, 19/08/2026): to change when handeling settlements filters
        }}
        noData={{
          hasNoData: !hasBankAccount || !hasSettlement,
          message: getEmptyStateMessage(hasBankAccount),
        }}
      />
    </div>
  )
}
