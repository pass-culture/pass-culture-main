import React from 'react'

import { EducationalInstitutionResponseModel } from 'apiClient/v1'

import styles from '../../OfferItem.module.scss'

const OfferInstitutionCell = ({
  educationalInstitution,
}: {
  educationalInstitution?: EducationalInstitutionResponseModel | null
}) => {
  return (
    <td className={styles['institution-column']}>
      {educationalInstitution?.name ?? 'Tous les établissements'}
    </td>
  )
}

export default OfferInstitutionCell
