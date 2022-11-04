import React from 'react'

import { EducationalInstitutionResponseModel } from 'apiClient/v1'
import { SummaryLayout } from 'components/SummaryLayout'

interface ICollectiveOfferStockSectionProps {
  institution?: EducationalInstitutionResponseModel | null
}

const CollectiveOfferStockSection = ({
  institution,
}: ICollectiveOfferStockSectionProps) => {
  const getVisibilityDescription = (
    institution?: EducationalInstitutionResponseModel | null
  ) => {
    if (!institution) {
      return 'Tous les établissements'
    }

    return (
      <>
        {institution.institutionType} {institution.name}
        <br />
        {institution.postalCode} {institution.city}
        <br />
        UAI : {institution.institutionId}
      </>
    )
  }

  return (
    <>
      <SummaryLayout.Row
        title="Visibilité de l’offre"
        description={getVisibilityDescription(institution)}
      />
    </>
  )
}

export default CollectiveOfferStockSection
