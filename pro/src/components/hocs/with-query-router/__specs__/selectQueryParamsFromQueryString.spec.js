import { selectQueryParamsFromQueryString } from '../selectQueryParamsFromQueryString'

describe('selectQueryParamsFromQueryString', () => {
  it('parses a query string with memoized buffer', () => {
    // given
    const searchParams = '/test?page=1&keywords=test&orderBy=offer.id+desc'

    // when
    const result = selectQueryParamsFromQueryString(searchParams)

    // then
    expect(result['/test?page']).toBe('1')
    expect(result.keywords).toBe('test')
    expect(result.orderBy).toBe('offer.id desc')
  })
})
