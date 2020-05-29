import * as fetch from '../../utils/fetch'
import { fetchAllVenuesByProUser } from '../venuesService'

describe('src | services | venuesService', () => {
  let mockJsonPromise

  beforeEach(() => {
    mockJsonPromise = Promise.resolve([{
      id: 'AE',
      name: 'Librairie Kléber',
      isVirtual: false
    }])
    jest
      .spyOn(fetch, 'fetchFromApiWithCredentials')
      .mockImplementation(() => mockJsonPromise)
  })

  it('should return paginatedBookingsRecap value', async () => {
    // When
    const venues = await fetchAllVenuesByProUser()

    // Then
    expect(venues).toHaveLength(1)
    expect(venues[0]).toStrictEqual({
      id: 'AE',
      name: 'Librairie Kléber',
      isVirtual: false
    })
  })

  it('should return empty paginatedBookingsRecap when an error occurred', async () => {
    // Given
    mockJsonPromise = Promise.reject('An error occured')

    // When
    const venues = await fetchAllVenuesByProUser()

    // Then
    expect(venues).toHaveLength(0)
  })
})
