import classNames from 'classnames'

import { EducationalInstitutionResponseModel } from 'apiClient/v1'
import styles from 'styles/components/Cells.module.scss'

interface OfferInstitutionCellProps {
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

  let showEducationalInstitution = '-'

  if (name) {
    showEducationalInstitution = name
  } else if (institutionType || city) {
    showEducationalInstitution = `${institutionType} ${city}`
  }

  return (
    <div
      className={classNames(
        styles['offers-table-cell'],
        styles['institution-column'],
        className
      )}
    >
      {showEducationalInstitution}
    </div>
  )
}
