import type {
  EducationalInstitutionResponseModel,
  EducationalRedactorResponseModel,
} from '@/apiClient/v1'
import {
  type Description,
  SummaryDescriptionList,
} from '@/ui-kit/SummaryLayout/SummaryDescriptionList'

interface CollectiveOfferInstitutionSectionProps {
  institution?: EducationalInstitutionResponseModel | null
  teacher?: EducationalRedactorResponseModel | null
}

export const CollectiveOfferInstitutionSection = ({
  institution,
  teacher,
}: CollectiveOfferInstitutionSectionProps) => {
  const getInstitutionDescription = (
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

  const descriptions: Description[] = [
    {
      title: 'Établissement scolaire auquel vous adressez votre offre',
      text: getInstitutionDescription(institution),
      stacked: true,
    },
  ]
  if (teacher) {
    descriptions.push({
      title: 'Enseignant avec qui vous avez construit cette offre',
      text: `${teacher.firstName} ${teacher.lastName}`,
      stacked: true,
    })
  }

  return <SummaryDescriptionList descriptions={descriptions} />
}
