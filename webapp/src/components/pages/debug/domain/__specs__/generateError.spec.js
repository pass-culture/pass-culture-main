import { generateError } from '../generateError'

describe('debugPage | domain | generateError', () => {
  describe('generateError', () => {
    it('should raise an error', () => {
      // When
      expect(generateError).toThrow('Generated error from Debug page')
    })
  })
})
