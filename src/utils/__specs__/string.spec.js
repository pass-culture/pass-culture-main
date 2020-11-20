import { getRequestErrorStringFromErrors, queryStringToObject } from '../string'

describe('getRequestErrorStringFromErrors', () => {
  const arrayOfObject1 = [{ global: 'toto' }]

  const arrayOfObject2 = [{ global: 'toto' }, { booking: 'titi' }]

  const objectWithArrays1 = {
    global: ['toto'],
  }

  const objectWithArrays2 = {
    booking: ['tata'],
    global: ['toto', 'titi'],
  }

  const noErrror = {}

  it('parse array of objects', () => {
    expect(getRequestErrorStringFromErrors(arrayOfObject1)).toBe('toto')
    expect(getRequestErrorStringFromErrors(arrayOfObject2)).toBe('toto titi')
  })

  it('parse hash with arrays', () => {
    expect(getRequestErrorStringFromErrors(objectWithArrays1)).toBe('toto')
    expect(getRequestErrorStringFromErrors(objectWithArrays2)).toBe('tata toto titi')
  })

  it('parse empty error', () => {
    expect(getRequestErrorStringFromErrors(noErrror)).toBe('')
  })
})

describe('queryStringToObject', () => {
  it('should return an empty object when given a string with query params', () => {
    const queryString =
      'distance=50&latitude=48.863779099999995&longitude=2.3374663&mots-cles=conspiration&page=1'
    const expected = {
      distance: '50',
      latitude: '48.863779099999995',
      longitude: '2.3374663',
      'mots-cles': 'conspiration',
      page: '1',
    }
    expect(queryStringToObject(queryString)).toStrictEqual(expected)
  })
})
