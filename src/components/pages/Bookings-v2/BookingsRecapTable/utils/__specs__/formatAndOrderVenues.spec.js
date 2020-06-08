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
})
