/* eslint no-console: 0, max-nested-callbacks: 0 */
import { getQueryParams, getQueryURL } from './getQueryParams'

describe('getQueryParams', () => {
  beforeEach(() => {})
  afterEach(() => {})
  describe('les parametres ne sont pas valides', () => {
    it('retoune une chaine vide', () => {
      const expected = ''
      let value = { params: { mediationId: null, offerId: null } }
      let result = getQueryParams(value)
      expect(expected).toEqual(result)
      value = { params: null }
      result = getQueryParams(value)
      expect(expected).toEqual(result)
      value = {}
      result = getQueryParams(value)
      expect(expected).toEqual(result)
      value = []
      result = getQueryParams(value)
      expect(expected).toEqual(result)
      value = false
      result = getQueryParams(value)
      expect(expected).toEqual(result)
      value = true
      result = getQueryParams(value)
      expect(expected).toEqual(result)
      value = null
      result = getQueryParams(value)
      expect(expected).toEqual(result)
      value = undefined
      result = getQueryParams(value)
      expect(expected).toEqual(result)
      value = 42
      result = getQueryParams(value)
      expect(expected).toEqual(result)
      value = new Error('unexpected')
      result = getQueryParams(value)
      expect(expected).toEqual(result)
    })
  })
  describe('uniquement offerId est défini', () => {
    it('retoune une chaine avec offerId uniquement', () => {
      const expected = 'offerId=1234'
      let value = { offerId: '1234' }
      let result = getQueryParams(value)
      expect(expected).toEqual(result)
      value = { params: { offerId: '1234' } }
      result = getQueryParams(value)
      expect(expected).toEqual(result)
    })
    it('retoune une chaine vide si offerId est egal a tuto', () => {
      const expected = ''
      let value = { offerId: 'tuto' }
      let result = getQueryParams(value)
      expect(expected).toEqual(result)
      value = { params: { offerId: 'tuto' } }
      result = getQueryParams(value)
      expect(expected).toEqual(result)
    })
    it('retoune une chaine vide si offerId est null ou non-string', () => {
      const expected = ''
      let value = { offerId: null }
      let result = getQueryParams(value)
      expect(expected).toEqual(result)
      value = { params: { offerId: null } }
      result = getQueryParams(value)
      expect(expected).toEqual(result)
      value = { params: { offerId: [] } }
      result = getQueryParams(value)
      expect(expected).toEqual(result)
    })
  })
  describe('uniquement mediationId est défini', () => {
    it('retoune une chaine avec mediationId uniquement', () => {
      const expected = 'mediationId=1234'
      let value = { mediationId: '1234' }
      let result = getQueryParams(value)
      expect(expected).toEqual(result)
      value = { params: { mediationId: '1234' } }
      result = getQueryParams(value)
      expect(expected).toEqual(result)
    })
    it('retoune une chaine vide si mediationId est null ou non-string', () => {
      const expected = ''
      let value = { mediationId: null }
      let result = getQueryParams(value)
      expect(expected).toEqual(result)
      value = { params: { mediationId: null } }
      result = getQueryParams(value)
      expect(expected).toEqual(result)
      value = { params: { mediationId: [] } }
      result = getQueryParams(value)
      expect(expected).toEqual(result)
    })
  })
  describe('mediationId et offerId sont définis', () => {
    it('retoune une chaine avec offerId & mediationId', () => {
      let expected = 'offerId=1234&mediationId=5678'
      let value = { mediationId: '5678', offerId: '1234' }
      let result = getQueryParams(value)
      expect(expected).toEqual(result)
      value = { params: { mediationId: '5678', offerId: '1234' } }
      result = getQueryParams(value)
      expect(expected).toEqual(result)
      expected = 'offerId=1234&mediationId=null'
      value = { params: { mediationId: 'null', offerId: '1234' } }
      result = getQueryParams(value)
      expect(expected).toEqual(result)
      expected = 'offerId=null&mediationId=1234'
      value = { params: { mediationId: '1234', offerId: 'null' } }
      result = getQueryParams(value)
      expect(expected).toEqual(result)
    })
  })
  describe('mediationId et offerId sont définis et offerId === tuto', () => {
    it('retoune uniquement mediationId', () => {
      const expected = 'mediationId=5678'
      const value = { mediationId: '5678', offerId: 'tuto' }
      const result = getQueryParams(value)
      expect(expected).toEqual(result)
    })
  })
  describe('mediationId et offerId sont définis et mediationId === vue', () => {
    it('retoune uniquement offerId', () => {
      let expected = 'offerId=1234'
      let value = { mediationId: 'booking', offerId: '1234' }
      let result = getQueryParams(value)
      expect(expected).toEqual(result)
      expected = 'offerId=1234'
      value = { mediationId: 'verso', offerId: '1234' }
      result = getQueryParams(value)
      expect(expected).toEqual(result)
    })
  })
})

describe('getQueryURL', () => {
  it('retoune une chaine avec offerId & mediationId splitted avec /', () => {
    const expected = '1234/5678'
    const value = { mediationId: '5678', offerId: '1234' }
    const result = getQueryURL(value)
    expect(expected).toEqual(result)
  })
})
