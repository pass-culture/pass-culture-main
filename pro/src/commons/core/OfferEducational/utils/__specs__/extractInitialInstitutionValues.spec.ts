import type { EducationalInstitutionResponseModel } from '@/apiClient/v1'
import { extractInitialInstitutionValues } from '@/commons/core/OfferEducational/utils/extractInitialInstitutionValues'
import { defaultGetCollectiveOfferRequest } from '@/commons/utils/factories/collectiveApiFactories'

describe('extractInitialInstitutionValues', () => {
  it('should return default values when institution is not defined', () => {
    expect(extractInitialInstitutionValues(null)).toStrictEqual({
      visibility: 'all',
      institution: '',
      teacher: '',
    })
  })

  it('should return institution details', () => {
    const institution: EducationalInstitutionResponseModel = {
      id: 1,
      name: 'Collège Bellevue',
      city: 'Alès',
      postalCode: '30100',
      phoneNumber: '',
      institutionId: 'ABCDEF11',
    }
    expect(extractInitialInstitutionValues(institution)).toStrictEqual({
      visibility: 'one',
      institution: '1',
      teacher: '',
    })
  })

  it('should return teacher details when institution and teacher are defined', () => {
    const institution: EducationalInstitutionResponseModel = {
      id: 1,
      name: 'Collège Bellevue',
      city: 'Alès',
      postalCode: '30100',
      phoneNumber: '',
      institutionId: 'ABCDEF11',
    }
    const teacher = {
      firstName: 'Reda',
      lastName: 'Khteur',
      civility: 'Mr.',
      email: 'reda.khteur@example.com',
    }
    expect(extractInitialInstitutionValues(institution, teacher)).toStrictEqual(
      {
        visibility: 'one',
        institution: '1',
        teacher: 'reda.khteur@example.com',
      }
    )
  })

  it('should return teacher details when institution and teacher are defined from requested informations', () => {
    const requestInformations = {
      ...defaultGetCollectiveOfferRequest,
      redactor: {
        firstName: 'Reda',
        lastName: 'Khteur',
        email: 'reda.khteur@example.com',
      },
    }
    expect(
      extractInitialInstitutionValues(null, null, requestInformations)
    ).toStrictEqual({
      visibility: 'one',
      institution: '',
      teacher: 'reda.khteur@example.com',
    })
  })
})
