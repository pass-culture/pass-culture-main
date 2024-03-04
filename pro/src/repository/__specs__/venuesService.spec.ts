import { venueListItemFactory } from 'utils/individualApiFactories'

import { computeVenueDisplayName, formatAndOrderVenues } from '../venuesService'

describe('formatAndOrderVenues', () => {
  it('should sort venues alphabetically', () => {
    const venues = [
      venueListItemFactory({
        id: 1,
        name: 'Offre numérique',
        offererName: 'gilbert Joseph',
        isVirtual: true,
      }),
      venueListItemFactory({
        id: 1,
        name: 'a venue name',
        publicName: 'Librairie Fnac',
        offererName: 'gilbert Joseph',
        isVirtual: false,
      }),
    ]

    const sortingValues = formatAndOrderVenues(venues)

    expect(sortingValues).toStrictEqual([
      {
        label: 'gilbert Joseph - Offre numérique',
        value: venues[1].id.toString(),
      },
      {
        label: 'Librairie Fnac',
        value: venues[0].id.toString(),
      },
    ])
  })

  it('should format venue option with "offerer name - offre numérique" when venue is virtual', () => {
    const venues = [
      venueListItemFactory({
        id: 1,
        name: 'Offre numérique',
        offererName: 'gilbert Joseph',
        isVirtual: true,
      }),
    ]

    const formattedValues = formatAndOrderVenues(venues)

    expect(formattedValues).toStrictEqual([
      {
        label: 'gilbert Joseph - Offre numérique',
        value: venues[0].id.toString(),
      },
    ])
  })
})

describe('computeVenueDisplayName', () => {
  it('should give venue name when venue is not virtual and has no public name', () => {
    const venue = {
      id: 12,
      name: 'Librairie Fnac',
      offererName: 'gilbert Joseph',
      isVirtual: false,
    }

    const computedVenueDisplayName = computeVenueDisplayName(venue)

    expect(computedVenueDisplayName).toBe('Librairie Fnac')
  })

  it('should give venue public name when venue is not virtual and has a public name', () => {
    const venue = {
      id: 12,
      name: 'Librairie Fnac',
      offererName: 'gilbert Joseph',
      publicName: 'Ma petite librairie',
      isVirtual: false,
    }

    const computedVenueDisplayName = computeVenueDisplayName(venue)

    expect(computedVenueDisplayName).toBe('Ma petite librairie')
  })

  it('should give the offerer name with "- Offre numérique" when venue is virtual', () => {
    const venue = {
      id: 12,
      name: 'Librairie Fnac',
      offererName: 'gilbert Joseph',
      isVirtual: true,
    }

    const computedVenueDisplayName = computeVenueDisplayName(venue)

    expect(computedVenueDisplayName).toBe('gilbert Joseph - Offre numérique')
  })
})
