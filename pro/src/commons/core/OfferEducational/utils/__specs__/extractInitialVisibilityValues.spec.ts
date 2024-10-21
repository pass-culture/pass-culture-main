import {
  EducationalInstitutionResponseModel,
  GetCollectiveOfferRequestResponseModel,
} from 'apiClient/v1'

import { extractInitialVisibilityValues } from '../extractInitialVisibilityValues'

describe('extractInitialVisibilityValues', () => {
  it('should return default values when institution is not defined', () => {
    expect(extractInitialVisibilityValues(null)).toStrictEqual({
      visibility: 'all',
      institution: '',
      'search-institution': '',
      'search-teacher': '',
      teacher: null,
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
    expect(extractInitialVisibilityValues(institution)).toStrictEqual({
      visibility: 'one',
      institution: '1',
      'search-institution': 'Collège Bellevue - Alès - ABCDEF11',
      'search-teacher': '',
      teacher: null,
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
    expect(extractInitialVisibilityValues(institution, teacher)).toStrictEqual({
      visibility: 'one',
      institution: '1',
      'search-institution': 'Collège Bellevue - Alès - ABCDEF11',
      'search-teacher': `${teacher.firstName} ${teacher.lastName}`,
      teacher: 'reda.khteur@example.com',
    })
  })

  it('should return teacher details when institution and teacher are defined from requested informations', () => {
    const requestInformations: GetCollectiveOfferRequestResponseModel = {
      comment: '',
      institution: {
        name: 'Collège Bellevue',
        city: 'Alès',
        postalCode: '30100',
        institutionId: 'ABCDEF11',
        institutionType: 'COLLEGE',
      },
      redactor: {
        firstName: 'Reda',
        lastName: 'Khteur',
        email: 'reda.khteur@example.com',
      },
    }
    expect(
      extractInitialVisibilityValues(null, null, requestInformations)
    ).toStrictEqual({
      visibility: 'one',
      institution: '',
      'search-institution': 'COLLEGE Collège Bellevue - Alès - ABCDEF11',
      'search-teacher': `Reda Khteur`,
      teacher: 'reda.khteur@example.com',
    })
  })
})
