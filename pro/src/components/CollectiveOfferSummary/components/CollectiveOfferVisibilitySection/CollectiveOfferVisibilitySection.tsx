import React from 'react'

import {
  EducationalInstitutionResponseModel,
  EducationalRedactorResponseModel,
} from 'apiClient/v1'
import { SummaryRow } from 'components/SummaryLayout/SummaryRow'

interface CollectiveOfferStockSectionProps {
  institution?: EducationalInstitutionResponseModel | null
  teacher?: EducationalRedactorResponseModel | null
}

const CollectiveOfferStockSection = ({
  institution,
  teacher,
}: CollectiveOfferStockSectionProps) => {
  const getVisibilityDescription = (
    institution?: EducationalInstitutionResponseModel | null
  ) => {
    if (!institution) {
      return <div>Tous les établissements</div>
    }

    return (
      <div>
        {institution.institutionType} {institution.name}
        <br />
        {institution.postalCode} {institution.city}
        <br />
        UAI : {institution.institutionId}
      </div>
    )
  }

  return (
    <>
      <SummaryRow
        title="Établissement scolaire auquel vous adressez votre offre"
        description={getVisibilityDescription(institution)}
      />
      {teacher && (
        <SummaryRow
          title="Enseignant avec qui vous avez construit cette offre"
          description={
            <div>
              {teacher.firstName} {teacher.lastName}
            </div>
          }
        />
      )}
    </>
  )
}

export default CollectiveOfferStockSection
