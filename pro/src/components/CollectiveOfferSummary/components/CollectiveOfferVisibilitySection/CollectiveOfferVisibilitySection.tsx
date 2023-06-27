import React from 'react'

import {
  EducationalInstitutionResponseModel,
  EducationalRedactorResponseModel,
} from 'apiClient/v1'
import { SummaryLayout } from 'components/SummaryLayout'

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
      <SummaryLayout.Row
        title="Établissement scolaire qui peut voir votre offre"
        description={getVisibilityDescription(institution)}
      />
      {teacher && (
        <SummaryLayout.Row
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
