import { closeSharePopin, openSharePopin } from '../share'

describe('actions | share', () => {
  describe('openSharePopin', () => {
    it('should return correct action type', () => {
      // when
      const action = openSharePopin()
      const expected = {
        type: 'TOGGLE_SHARE_POPIN',
      }

      // then
      expect(action).toMatchObject(expected)
    })
  })

  describe('closeSharePopin', () => {
    it('should return correct action type', () => {
      // when
      const action = closeSharePopin()
      const expected = {
        options: null,
        type: 'TOGGLE_SHARE_POPIN',
      }

      // then
      expect(action).toMatchObject(expected)
    })
  })
})
