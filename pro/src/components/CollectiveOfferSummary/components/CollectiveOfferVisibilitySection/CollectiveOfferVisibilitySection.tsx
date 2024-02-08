import React from 'react'

import {
  EducationalInstitutionResponseModel,
  EducationalRedactorResponseModel,
} from 'apiClient/v1'
import {
  Description,
  SummaryDescriptionList,
} from 'components/SummaryLayout/SummaryDescriptionList'

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

  const descriptions: Description[] = [
    {
      title: 'Établissement scolaire auquel vous adressez votre offre',
      text: getVisibilityDescription(institution),
    },
  ]
  if (teacher) {
    descriptions.push({
      title: 'Enseignant avec qui vous avez construit cette offre',
      text: (
        <div>
          {teacher.firstName} {teacher.lastName}
        </div>
      ),
    })
  }

  return <SummaryDescriptionList descriptions={descriptions} />
}

export default CollectiveOfferStockSection
