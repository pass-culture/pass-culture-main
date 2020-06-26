import formatAndOrderVenues from '../formatAndOrderVenues'

describe('formatAndOrderVenues', () => {
  it('should sort venues alphabetically', () => {
    // given
    const venues = [
      { id: 'AF', name: 'Librairie Fnac', offererName: 'gilbert Joseph', isVirtual: false },
      { id: 'AE', name: 'Offre numérique', offererName: 'gilbert Joseph', isVirtual: true },
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
      { id: 'AE', name: 'Offre numérique', offererName: 'gilbert Joseph', isVirtual: true },
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
