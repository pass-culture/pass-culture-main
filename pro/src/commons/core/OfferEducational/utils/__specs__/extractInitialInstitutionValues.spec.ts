import type { EducationalInstitutionResponseModel } from '@/apiClient/v1'
import { defaultGetCollectiveOfferRequest } from '@/commons/utils/factories/collectiveApiFactories'

import { extractInitialInstitutionValues } from '../extractInitialInstitutionValues'

describe('extractInitialInstitutionValues', () => {
  it('should return default values when institution is not defined', () => {
    expect(extractInitialInstitutionValues(null)).toStrictEqual({
      educationalInstitution: '',
      teacherEmail: '',
      teacherName: '',
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
      institutionType: 'Collège',
    }
    expect(extractInitialInstitutionValues(institution)).toStrictEqual({
      educationalInstitution: '1',
      teacherEmail: '',
      teacherName: '',
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
      institutionType: 'Collège',
    }
    const teacher = {
      firstName: 'Reda',
      lastName: 'Khteur',
      civility: 'Mr.',
      email: 'reda.khteur@example.com',
    }
    expect(extractInitialInstitutionValues(institution, teacher)).toStrictEqual(
      {
        educationalInstitution: '1',
        teacherEmail: 'reda.khteur@example.com',
        teacherName: 'Reda Khteur',
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
      educationalInstitution: '',
      teacherEmail: 'reda.khteur@example.com',
      teacherName: 'Reda Khteur',
    })
  })
})
