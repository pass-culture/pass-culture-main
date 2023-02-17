import { EducationalInstitutionResponseModel } from 'apiClient/v1'

import { extractInitialVisibilityValues } from '../extractInitialVisibilityValues'

describe('extractInitialVisibilityValues', () => {
  it('should return default values when institution is not defined', () => {
    expect(extractInitialVisibilityValues(null)).toStrictEqual({
      institution: '',
      'search-institution': '',
      visibility: 'all',
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
      institution: '1',
      'search-institution': 'Collège Bellevue - Alès',
      visibility: 'one',
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
      institution: '1',
      'search-institution': 'Collège Bellevue - Alès',
      visibility: 'one',
      'search-teacher': `${teacher.firstName} ${teacher.lastName}`,
      teacher: 'reda.khteur@example.com',
    })
  })
})
