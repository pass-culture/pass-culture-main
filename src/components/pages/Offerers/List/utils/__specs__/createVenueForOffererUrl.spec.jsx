import createVenueForOffererUrl from '../createVenueForOffererUrl'

describe('src | components | pages | Offerers | decorators | createVenueForOffererUrl', () => {
  it('should return an empty string when no offerers', () => {
    // given
    const offerers = []

    // when
    const result = createVenueForOffererUrl(offerers)

    // then
    const expected = ''
    expect(result).toStrictEqual(expected)
  })

  it("should return an url with first offerer's id when two offerers are given", () => {
    // given
    const offerers = [{ id: 'CQ' }, { id: 'FT' }]

    // when
    const result = createVenueForOffererUrl(offerers)

    // then
    const expected = '/structures/CQ/lieux/creation'
    expect(result).toStrictEqual(expected)
  })
})
