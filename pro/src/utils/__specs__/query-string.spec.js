import { parse, stringify } from 'utils/query-string'

describe('handling of URL', () => {
  it('should transform queryParams to object / keys-values', () => {
    // Given
    const queryParams = '?offerId=ME&stockId=FA&mediation&name=un+titre'

    // When
    const string = parse(queryParams)

    // Then
    expect(string).toStrictEqual({
      offerId: 'ME',
      stockId: 'FA',
      mediation: '',
      name: 'un titre',
    })
  })

  it('shoudl transform an object to query string', () => {
    // Given
    const queryParams = {
      offerId: 'ME',
      stockId: 'FA',
      mediation: '',
      name: 'un titre',
    }

    // When
    const string = stringify(queryParams)

    // Then
    expect(string).toBe('offerId=ME&stockId=FA&mediation=&name=un+titre')
  })
})
