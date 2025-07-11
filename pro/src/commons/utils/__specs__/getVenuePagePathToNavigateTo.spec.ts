import { getVenuePagePathToNavigateTo } from '../getVenuePagePathToNavigateTo'

describe('getVenuePagePathToNavigateTo', () => {
  it('should preserve the base path as context to differentiate address / adage / partner pages and append subPath', () => {
    const offererId = '123'
    const venueId = '456'
    const subPath = '/parametres'
    const originalPath = `/structures/${offererId}/lieux/${venueId}/page-partenaire`
    const expectedPath = `${originalPath}${subPath}`

    Object.defineProperty(window, 'location', {
      value: { pathname: originalPath },
    })

    expect(getVenuePagePathToNavigateTo(offererId, venueId, subPath)).toBe(
      expectedPath
    )
  })
})
