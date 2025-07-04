import { EducationalInstitutionResponseModel } from 'apiClient/v1'

interface OfferInstitutionCellProps {
  rowId: string
  educationalInstitution?: EducationalInstitutionResponseModel | null
  className?: string
}

export const OfferInstitutionCell = ({
  educationalInstitution,
}: OfferInstitutionCellProps) => {
  const { name, institutionType, city } = educationalInstitution || {}

  let showEducationalInstitution = '-'

  if (name) {
    showEducationalInstitution = name
  } else if (institutionType || city) {
    showEducationalInstitution = `${institutionType} ${city}`
  }

  return <div>{showEducationalInstitution}</div>
}
