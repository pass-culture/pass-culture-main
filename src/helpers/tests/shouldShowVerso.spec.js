import shouldShowVerso from '../shouldShowVerso'

describe('src | helpers | isVersoView', () => {
  describe('that match is a valid object', () => {
    it('should return false if match is undefined', () => {
      // given
      const obj = undefined

      // when
      const result = shouldShowVerso(obj)

      // then
      const expected = false
      expect(result).toEqual(expected)
    })

    it('should return false if match a string', () => {
      // given
      const obj = 'this is a string'

      // when
      const result = shouldShowVerso(obj)

      // then
      const expected = false
      expect(result).toEqual(expected)
    })

    it('should return false if match is an array', () => {
      // given
      const obj = []

      // when
      const result = shouldShowVerso(obj)

      // then
      const expected = false
      expect(result).toEqual(expected)
    })
  })

  describe('that match should have a params property', () => {
    it('should return false if params property is undefined', () => {
      // given
      const obj = {}

      // when
      const result = shouldShowVerso(obj)

      // then
      const expected = false
      expect(result).toEqual(expected)
    })

    it('should return false if params property is null', () => {
      // given
      const obj = { params: null }

      // when
      const result = shouldShowVerso(obj)

      // then
      const expected = false
      expect(result).toEqual(expected)
    })

    it('should return false if params property is not an object', () => {
      // given
      const obj = { params: 'this is a string' }

      // when
      const result = shouldShowVerso(obj)

      // then
      const expected = false
      expect(result).toEqual(expected)
    })
  })

  describe('with properties mediationId and view from match.params object', () => {
    it('should return false if missing both', () => {
      // given
      const obj = { params: {} }

      // when
      const result = shouldShowVerso(obj)

      // then
      const expected = false
      expect(result).toEqual(expected)
    })

    it('should return false if mediationId and view property are null', () => {
      // given
      const obj = {
        params: {
          mediationId: null,
          view: null,
        },
      }

      // when
      const result = shouldShowVerso(obj)

      // then
      const expected = false
      expect(result).toEqual(expected)
    })

    it('should return false if mediationId is not equal to verso', () => {
      // given
      const obj = {
        params: {
          mediationId: 'AAAA',
          view: 'another_view',
        },
      }

      // when
      const result = shouldShowVerso(obj)

      // then
      const expected = false
      expect(result).toEqual(expected)
    })

    it('should return true if mediationId equals verso', () => {
      // given
      const obj = {
        params: {
          mediationId: 'verso',
          view: 'another_view',
        },
      }

      // when
      const result = shouldShowVerso(obj)

      // then
      const expected = true
      expect(result).toEqual(expected)
    })

    it('should return true if view equals verso', () => {
      // given
      const obj = {
        params: {
          mediationId: 'AAAA',
          view: 'verso',
        },
      }

      // when
      const result = shouldShowVerso(obj)

      // then
      const expected = true
      expect(result).toEqual(expected)
    })
  })
})
