import { isValidUrlWithTemplateStrings } from '../isValidUrlWithTemplateStrings'

describe('isValidUrlWithTemplateStrings', () => {
  describe('with valid URLs', () => {
    it.each([
      ['http://example.com'],
      ['https://example.com'],
      ['https://www.example.com'],
      ['https://example.com:8080'],
      ['https://example.com/path/to/page'],
      ['https://example.com?foo=bar&baz=qux'],
      ['https://example.com/page#section'],
      ['https://api.v2.example.com'],
      ['https://example.museum'],
      ['https://example.photography'],
      ['http://192.168.1.1'],
      ['http://127.0.0.1:3000'],
      ['https://my-example-site.com'],
      ['https://example.com/path%20with%20spaces'],
      ['https://passculture.app/offer/12345'],
    ])('should accept %s', (url) => {
      expect(isValidUrlWithTemplateStrings(url)).toBe(true)
    })
  })

  describe('with template variables', () => {
    it.each([
      ['https://example.com/{id}', 'simple variable'],
      ['https://example.com/{user_id}', 'underscore in variable'],
      ['https://example.com/{offer123}', 'number in variable'],
      ['https://example.com/{OFFER_ID}', 'uppercase variable'],
      ['https://example.com/{resource}/{id}', 'multiple variables'],
      ['https://example.com?token={token}', 'variable in query'],
      [
        'https://example.org/?email={email}&offerID={offerId}&token={token}',
        'multiple variables in query',
      ],
    ])('should accept %s (%s)', (url) => {
      expect(isValidUrlWithTemplateStrings(url)).toBe(true)
    })
  })

  describe('with invalid URLs', () => {
    it.each([
      ['', 'empty string'],
      ['   ', 'whitespace only'],
      ['example.com', 'missing protocol'],
      ['www.example.com', 'www without protocol'],
      ['https://', 'protocol only'],
      ['https://example .com', 'space in domain'],
      ['https://example..com', 'double dots in domain'],
      ['mailto:test@example.com', 'mailto protocol'],
      [' https://example.com', 'leading space'],
      ['https://example.com ', 'trailing space'],
    ])('should reject %s (%s)', (url) => {
      expect(isValidUrlWithTemplateStrings(url)).toBe(false)
    })
  })

  describe('with edge cases', () => {
    it('should reject localhost (yup limitation, backend validates)', () => {
      expect(isValidUrlWithTemplateStrings('http://localhost:3000')).toBe(false)
    })

    it('should handle long repeated string without hanging (no ReDoS)', () => {
      const longString = 'a'.repeat(100)
      expect(isValidUrlWithTemplateStrings(`https://${longString}`)).toBe(false)
    })
  })
})
