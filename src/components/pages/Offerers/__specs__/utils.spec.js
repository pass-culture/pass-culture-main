import createVenueForOffererUrl from '../utils'

describe('src | components | pages | Offerers | decorators | createVenueForOffererUrl', () => {
  it("should return an empty string", () => {
    // given
    const offerers = []

    // when
    const expected = ""
    const result = createVenueForOffererUrl(offerers)

    // then
    expect(result).toEqual(expected)
  })
  it("should return url with first offerer's id", () => {
    // given
    const offerers = [
      {
      id: "CQ"
    },
    {
      id: "FT"
    }
  ]

    // when
    const expected = "/structures/CQ/lieux/creation"
    const result = createVenueForOffererUrl(offerers)

    // then
    expect(result).toEqual(expected)
  })
})
