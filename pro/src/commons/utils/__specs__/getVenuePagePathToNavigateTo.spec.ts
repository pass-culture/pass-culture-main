import { getVenuePagePathToNavigateTo } from '../getVenuePagePathToNavigateTo'

describe('getVenuePagePathToNavigateTo', () => {
  it('should preserve the base path as context to differentiate address / adage / partner pages and append subPath', () => {
    const offererId = '123'
    const venueId = '456'
    const subPath = '/parametres'
    const originalPath = `/structures/${offererId}/lieux/${venueId}/page-partenaire`
    const expectedPath = `${originalPath}${subPath}`

    vi.spyOn(window, 'location', 'get').mockReturnValue({
      ...window.location,
      pathname: originalPath,
    })

    expect(getVenuePagePathToNavigateTo(offererId, venueId, subPath)).toBe(
      expectedPath
    )
  })
})
