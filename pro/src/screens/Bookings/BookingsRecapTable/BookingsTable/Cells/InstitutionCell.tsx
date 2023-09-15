import React from 'react'

import { EducationalInstitutionResponseModel } from 'apiClient/v1'

import styles from './CellFormatter.module.scss'

interface InstitutionCellProps {
  institution: EducationalInstitutionResponseModel
}

export const InstitutionCell = ({ institution }: InstitutionCellProps) => {
  const institutionName =
    `${institution.institutionType} ${institution.name}`.trim()
  const institutionAddress =
    `${institution.postalCode} ${institution.city}`.trim()

  return (
    <div>
      <div>
        <span>{institutionName}</span>
        <br />
      </div>
      <span className={styles['institution-cell-subtitle']}>
        {institutionAddress}
      </span>
    </div>
  )
}
