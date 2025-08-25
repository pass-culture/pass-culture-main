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

  const getInstitutionLabel = () => {
    if (name && postalCode) {
      return `${name} - ${postalCode}`
    }
    if (institutionType || city) {
      return `${institutionType} ${city}`
    }

    return 'Tous les établissements'
  }

  return (
    <td
      role="cell"
      className={classNames(
        styles['offers-table-cell'],
        styles['institution-column'],
        className
      )}
      headers={`${rowId} ${getCellsDefinition().INSTITUTION.id}`}
    >
      {getInstitutionLabel()}
    </td>
  )
}
