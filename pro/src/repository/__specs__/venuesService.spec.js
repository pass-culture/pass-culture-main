import { computeVenueDisplayName, formatAndOrderVenues } from '../venuesService'

describe('venuesService', () => {
  describe('formatAndOrderVenues', () => {
    it('should sort venues alphabetically', () => {
      // given
      const venues = [
        {
          id: 'AF',
          nonHumanizedId: 1,
          name: 'Librairie Fnac',
          offererName: 'gilbert Joseph',
          isVirtual: false,
        },
        {
          id: 'AE',
          nonHumanizedId: 2,
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
          id: venues[1].nonHumanizedId.toString(),
        },
        {
          displayName: 'Librairie Fnac',
          id: venues[0].nonHumanizedId.toString(),
        },
      ])
    })

    it('should format venue option with "offerer name - offre numérique" when venue is virtual', () => {
      // given
      const venues = [
        {
          id: 'AE',
          nonHumanizedId: 1,
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
          id: venues[0].nonHumanizedId.toString(),
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
