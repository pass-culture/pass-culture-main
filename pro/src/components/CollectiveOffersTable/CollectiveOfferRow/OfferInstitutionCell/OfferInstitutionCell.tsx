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
  const { name, institutionType, city } = educationalInstitution || {}

  let showEducationalInstitution = 'Tous les établissements'

  if (name) {
    showEducationalInstitution = name
  } else if (institutionType || city) {
    showEducationalInstitution = `${institutionType} ${city}`
  }

  return (
    <td
      // biome-ignore lint/a11y: accepted for assistive tech
      role="cell"
      className={classNames(
        styles['offers-table-cell'],
        styles['institution-column'],
        className
      )}
      headers={`${rowId} ${getCellsDefinition().INSTITUTION.id}`}
    >
      {showEducationalInstitution}
    </td>
  )
}
