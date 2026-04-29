import { getVenuePagePathToNavigateTo } from '../getVenuePagePathToNavigateTo'

describe('getVenuePagePathToNavigateTo', () => {
  it('should preserve the base path as context to differentiate address / adage / partner pages and append subPath', () => {
    const subPath = '/parametres'
    const originalPath = `/partenaire/page-partenaire`
    const expectedPath = `${originalPath}${subPath}`

    vi.spyOn(window, 'location', 'get').mockReturnValue({
      ...window.location,
      pathname: originalPath,
    })

    expect(getVenuePagePathToNavigateTo(subPath)).toBe(expectedPath)
  })

  it('should use page-collective context when path includes page-collective', () => {
    vi.spyOn(window, 'location', 'get').mockReturnValue({
      ...window.location,
      pathname: '/partenaire/page-collective',
    })

    expect(getVenuePagePathToNavigateTo('/edition')).toBe(
      '/partenaire/page-collective/edition'
    )
  })

  it('should use page-individuelle context when path does not include page-partenaire nor page-collective', () => {
    vi.spyOn(window, 'location', 'get').mockReturnValue({
      ...window.location,
      pathname: '/partenaire/page-individuelle',
    })

    expect(getVenuePagePathToNavigateTo()).toBe('/partenaire/page-individuelle')
  })
})
