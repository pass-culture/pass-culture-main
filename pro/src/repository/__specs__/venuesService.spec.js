import * as pcapi from 'repository/pcapi/pcapi'

import {
  computeVenueDisplayName,
  fetchAllVenuesByProUser,
  formatAndOrderVenues,
} from '../venuesService'

describe('venuesService', () => {
  let mockJsonPromise

  describe('fetchAllVenuesByProUser', () => {
    beforeEach(() => {
      mockJsonPromise = Promise.resolve([
        {
          id: 'AE',
          name: 'Librairie Kléber',
          isVirtual: false,
        },
      ])
      jest
        .spyOn(pcapi, 'getVenuesForOfferer')
        .mockImplementation(() => mockJsonPromise)
    })

    it('should return list of venues', async () => {
      // When
      const venues = await fetchAllVenuesByProUser()
      // Then
      expect(pcapi.getVenuesForOfferer).toHaveBeenCalledWith({
        offererId: undefined,
      })
      expect(venues).toHaveLength(1)
      expect(venues[0]).toStrictEqual({
        id: 'AE',
        name: 'Librairie Kléber',
        isVirtual: false,
      })
    })

    it('should call api with offererId in query params when given', async () => {
      // When
      await fetchAllVenuesByProUser('A4')

      // Then
      expect(pcapi.getVenuesForOfferer).toHaveBeenCalledWith({
        offererId: 'A4',
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

  describe('formatAndOrderVenues', () => {
    it('should sort venues alphabetically', () => {
      // given
      const venues = [
        {
          id: 'AF',
          name: 'Librairie Fnac',
          offererName: 'gilbert Joseph',
          isVirtual: false,
        },
        {
          id: 'AE',
          name: 'Offre numérique',
          offererName: 'gilbert Joseph',
          isVirtual: true,
        },
      ]

      // when
      const sortingValues = formatAndOrderVenues(venues)

      // then
      expect(sortingValues).toStrictEqual([
        {
          displayName: 'gilbert Joseph - Offre numérique',
          id: 'AE',
        },
        {
          displayName: 'Librairie Fnac',
          id: 'AF',
        },
      ])
    })

    it('should format venue option with "offerer name - offre numérique" when venue is virtual', () => {
      // given
      const venues = [
        {
          id: 'AE',
          name: 'Offre numérique',
          offererName: 'gilbert Joseph',
          isVirtual: true,
        },
      ]

      // when
      const formattedValues = formatAndOrderVenues(venues)

      // then
      expect(formattedValues).toStrictEqual([
        {
          displayName: 'gilbert Joseph - Offre numérique',
          id: 'AE',
        },
      ])
    })
  })

  describe('computeVenueDisplayName', () => {
    it('should give venue name when venue is not virtual and has no public name', () => {
      // given
      const venue = {
        id: 'AF',
        name: 'Librairie Fnac',
        offererName: 'gilbert Joseph',
        isVirtual: false,
      }

      // when
      const computedVenueDisplayName = computeVenueDisplayName(venue)

      // then
      expect(computedVenueDisplayName).toBe('Librairie Fnac')
    })

    it('should give venue public name when venue is not virtual and has a public name', () => {
      // given
      const venue = {
        id: 'AF',
        name: 'Librairie Fnac',
        offererName: 'gilbert Joseph',
        publicName: 'Ma petite librairie',
        isVirtual: false,
      }

      // when
      const computedVenueDisplayName = computeVenueDisplayName(venue)

      // then
      expect(computedVenueDisplayName).toBe('Ma petite librairie')
    })

    it('should give the offerer name with "- Offre numérique" when venue is virtual', () => {
      // given
      const venue = {
        id: 'AF',
        name: 'Librairie Fnac',
        offererName: 'gilbert Joseph',
        isVirtual: true,
      }

      // when
      const computedVenueDisplayName = computeVenueDisplayName(venue)

      // then
      expect(computedVenueDisplayName).toBe('gilbert Joseph - Offre numérique')
    })
  })
})
