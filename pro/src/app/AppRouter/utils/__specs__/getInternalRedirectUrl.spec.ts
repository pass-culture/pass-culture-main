import { getInternalRedirectUrl } from '../getInternalRedirectUrl'

describe('getInternalRedirectUrl', () => {
  it('should return the provided internal path', () => {
    expect(getInternalRedirectUrl('/accueil')).toBe('/accueil')
  })

  it('should preserve the requested internal path and query string', () => {
    expect(getInternalRedirectUrl('/offres?status=active')).toBe(
      '/offres?status=active'
    )
  })

  it('should add search params to the requested internal path', () => {
    expect(
      getInternalRedirectUrl('/offres?status=active', 'id-structure=123')
    ).toBe('/offres?status=active&id-structure=123')
  })

  it('should override matching search params with the provided values', () => {
    expect(
      getInternalRedirectUrl(
        '/offres?id-structure=456&status=active',
        'id-structure=123'
      )
    ).toBe('/offres?id-structure=123&status=active')
  })

  it('should add search params when the requested path has none', () => {
    expect(getInternalRedirectUrl('/offres', 'id-structure=123')).toBe(
      '/offres?id-structure=123'
    )
  })

  it('should preserve the requested hash when adding search params', () => {
    expect(getInternalRedirectUrl('/offres#details', 'id-structure=123')).toBe(
      '/offres?id-structure=123#details'
    )
  })

  it.each([
    ['absolute HTTP URL', 'http://evil.example/path'],
    ['absolute HTTPS URL', 'https://evil.example/path'],
    ['protocol-relative URL', '//evil.example/path'],
    ['three-leading-slashes URL', '///evil.example/path'],
    ['backslash-prefixed URL', String.raw`\\evil.example\path`],
    ['mixed slash and backslash URL', String.raw`/\\evil.example/path`],
    ['JavaScript scheme', 'javascript:alert(1)'],
    ['data scheme', 'data:text/html,redirect'],
    ['FTP scheme', 'ftp://evil.example/path'],
    ['mixed-case HTTP scheme', 'HtTpS://evil.example/path'],
    [
      'URL containing user information',
      'https://trusted.example@evil.example/path',
    ],
    ['scheme without authority slashes', 'https:evil.example/path'],
    ['percent-encoded protocol-relative URL', '%2F%2Fevil.example/path'],
    ['percent-encoded backslash URL', '%5C%5Cevil.example/path'],
  ])(
    'should keep the navigation on the current origin for %s',
    (_, redirectTo) => {
      // Simulate reading redirectTo from the query string, which decodes it once.
      const redirectToFromQuery = new URLSearchParams(
        `redirectTo=${redirectTo}`
      ).get('redirectTo')

      // Check whether this payload would escape without the normalization.
      expect(
        new URL(redirectToFromQuery ?? '', 'http://trusted.example').origin
      ).not.toBe('http://trusted.example')

      const nextUrl = getInternalRedirectUrl(redirectToFromQuery ?? '')

      expect(new URL(nextUrl, 'http://trusted.example').origin).toBe(
        'http://trusted.example'
      )
    }
  )
})
