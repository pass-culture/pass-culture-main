import { parse, stringify } from '@/commons/utils/query-string'

describe('handling of URL', () => {
  it('should transform queryParams to object / keys-values', () => {
    const queryParams = '?offerId=ME&stockId=FA&mediation&name=un+titre'

    const string = parse(queryParams)

    expect(string).toStrictEqual({
      offerId: 'ME',
      stockId: 'FA',
      mediation: '',
      name: 'un titre',
    })
  })

  it('shoudl transform an object to query string', () => {
    const queryParams = {
      offerId: 'ME',
      stockId: 'FA',
      mediation: '',
      name: 'un titre',
    }

    const string = stringify(queryParams)

    expect(string).toBe('offerId=ME&stockId=FA&mediation=&name=un+titre')
  })
})
