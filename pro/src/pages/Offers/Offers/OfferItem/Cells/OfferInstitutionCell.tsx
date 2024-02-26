import React from 'react'

import { EducationalInstitutionResponseModel } from 'apiClient/v1'

import styles from '../OfferItem.module.scss'

interface OfferInstitutionCellProps {
  educationalInstitution?: EducationalInstitutionResponseModel | null
}

export const OfferInstitutionCell = ({
  educationalInstitution,
}: OfferInstitutionCellProps) => {
  const { name, institutionType, city } = educationalInstitution || {}

  let showEducationalInstitution = 'Tous les établissements'

  if (name) {
    showEducationalInstitution = name
  } else if (institutionType || city) {
    showEducationalInstitution = `${institutionType} ${city}`
  }

  return (
    <td className={styles['institution-column']}>
      {showEducationalInstitution}
    </td>
  )
}
