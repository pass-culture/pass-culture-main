import type { EducationalDomainsResponseModel } from '@/apiClient/v1/new'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'

import { mapVenueDomains } from '../mapVenueDomains'

vi.mock('@/commons/errors/handleUnexpectedError', () => ({
  handleUnexpectedError: vi.fn(),
}))

const educationalDomains: EducationalDomainsResponseModel = [
  { id: 1, name: 'Danse', nationalPrograms: [] },
  { id: 2, name: 'Musique', nationalPrograms: [] },
]

describe('mapVenueDomains', () => {
  it('should return null when there is no educational domain at all', () => {
    const venue = makeGetVenueResponseModel({
      id: 1,
      collectiveDomains: [{ id: 1, name: 'Danse' }],
    })

    expect(mapVenueDomains(venue, [])).toEqual(['Non renseigné'])
  })

  it('should map venue collective domain ids to their label', () => {
    const venue = makeGetVenueResponseModel({
      id: 1,
      collectiveDomains: [
        { id: 1, name: 'Danse' },
        { id: 2, name: 'Musique' },
      ],
    })

    expect(mapVenueDomains(venue, educationalDomains)).toEqual([
      'Danse',
      'Musique',
    ])
  })

  it('should return a placeholder when the venue has no collective domain', () => {
    const venue = makeGetVenueResponseModel({ id: 1, collectiveDomains: [] })

    expect(mapVenueDomains(venue, educationalDomains)).toEqual([
      'Non renseigné',
    ])
  })

  it('should throw when a venue collective domain is missing from the API list', () => {
    const venue = makeGetVenueResponseModel({
      id: 1,
      collectiveDomains: [{ id: 99, name: 'Inconnu' }],
    })

    expect(() => mapVenueDomains(venue, educationalDomains)).toThrow()
  })
})
