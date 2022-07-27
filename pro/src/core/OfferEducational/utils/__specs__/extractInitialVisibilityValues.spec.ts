import { EducationalInstitutionResponseModel } from 'apiClient/v1'

import { extractInitialVisibilityValues } from '../extractInitialVisibilityValues'

describe('extractInitialVisibilityValues', () => {
  it('when insitution is null', () => {
    expect(extractInitialVisibilityValues(null)).toStrictEqual({
      institution: '',
      'search-institution': '',
      visibility: 'all',
    })
  })

  it('when institution is defined', () => {
    const institution: EducationalInstitutionResponseModel = {
      id: 1,
      name: 'Collège Bellevue',
      city: 'Alès',
      postalCode: '30100',
    }
    expect(extractInitialVisibilityValues(institution)).toStrictEqual({
      institution: '1',
      'search-institution': 'Collège Bellevue - Alès',
      visibility: 'one',
    })
  })
})
