import classNames from 'classnames'

import type { EducationalInstitutionResponseModel } from '@/apiClient/v1'
import { getCellsDefinition } from '@/components/CollectiveOffersTable/utils/cellDefinitions'

import styles from '../Cells.module.scss'

export interface OfferInstitutionCellProps {
  rowId: string
  educationalInstitution?: EducationalInstitutionResponseModel | null
  className?: string
}

export const OfferInstitutionCell = ({
  rowId,
  educationalInstitution,
  className,
}: OfferInstitutionCellProps) => {
  const { name, postalCode, institutionType, city } =
    educationalInstitution || {}

  const institutionLabel =
    name || [institutionType, city].filter(Boolean).join(' ') || '-'

  return (
    <td
      // biome-ignore lint/a11y: accepted for assistive tech
      role="cell"
      className={classNames(
        'cell-institution',
        styles['offers-table-cell'],
        styles['institution-column'],
        className
      )}
      headers={`${rowId} ${getCellsDefinition().INSTITUTION.id}`}
    >
      <div>
        <div className={styles['institution-label-ellipsis']}>
          {institutionLabel}
        </div>
        {postalCode && <div> {postalCode}</div>}
      </div>
    </td>
  )
}
