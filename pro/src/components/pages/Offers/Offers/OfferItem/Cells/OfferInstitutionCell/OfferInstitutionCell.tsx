import React from 'react'

import { EducationalInstitutionResponseModel } from 'apiClient/v1'

const OfferInstitutionCell = ({
  educationalInstitution,
}: {
  educationalInstitution?: EducationalInstitutionResponseModel | null
}) => {
  return (
    <td className="stock-column">
      {educationalInstitution?.name ?? 'Tous les établissements'}
    </td>
  )
}

export default OfferInstitutionCell
