import { api } from '@/apiClient/api'
import type {
  EducationalInstitutionResponseModel,
  EducationalInstitutionsResponseModel,
} from '@/apiClient/v1'

export const getEducationalInstitutions = async (): Promise<
  EducationalInstitutionResponseModel[]
> => {
  const allInstitutionsPromises: Promise<EducationalInstitutionsResponseModel>[] =
    []

  const fistPageResponse = await api.getEducationalInstitutions({
    query: { page: 1 },
  })
  let currentPage = fistPageResponse.page
  const totalPages = fistPageResponse.pages

  while (currentPage < totalPages) {
    currentPage += 1
    allInstitutionsPromises.push(
      api.getEducationalInstitutions({
        query: { page: currentPage },
      })
    )
  }

  const promisesResult: EducationalInstitutionResponseModel[] = (
    await Promise.all(allInstitutionsPromises)
  ).reduce((acc: EducationalInstitutionResponseModel[], response) => {
    acc.push(...response.educationalInstitutions)
    return acc
  }, [])

  return [...fistPageResponse.educationalInstitutions, ...promisesResult]
}
