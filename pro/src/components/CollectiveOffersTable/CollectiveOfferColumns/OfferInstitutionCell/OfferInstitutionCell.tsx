import type { EducationalInstitutionResponseModel } from '@/apiClient/v1'

import styles from './OfferInstitutionCell.module.scss'

export interface OfferInstitutionCellProps {
  educationalInstitution?: EducationalInstitutionResponseModel | null
}

export const OfferInstitutionCell = ({
  educationalInstitution,
}: OfferInstitutionCellProps) => {
  const { name, postalCode, institutionType, city } =
    educationalInstitution || {}

  const institutionLabel =
    name || [institutionType, city].filter(Boolean).join(' ') || '-'

  return (
    <div className={styles['institution-column']}>
      <p className={styles['institution-label-ellipsis']}>{institutionLabel}</p>
      {postalCode && (
        <p className={styles['institution-postal-code']}> {postalCode}</p>
      )}
    </div>
  )
}
