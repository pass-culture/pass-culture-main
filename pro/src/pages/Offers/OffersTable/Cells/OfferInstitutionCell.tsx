import classNames from 'classnames'

import { EducationalInstitutionResponseModel } from 'apiClient/v1'

import styles from './Cells.module.scss'

interface OfferInstitutionCellProps {
  educationalInstitution?: EducationalInstitutionResponseModel | null
  headers?: string
}

export const OfferInstitutionCell = ({
  educationalInstitution,
  headers,
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
      className={classNames(
        styles['offers-table-cell'],
        styles['institution-column']
      )}
      headers={headers}
    >
      {showEducationalInstitution}
    </td>
  )
}
