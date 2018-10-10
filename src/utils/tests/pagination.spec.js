import { windowToApiQuery } from '../pagination'

describe('src | utils | pagination ', () => {
  describe('src | utils | pagination ', () => {
    it('return false', () => {
      const queryString = {
        categories: 'Applaudir',
        date: null,
        jours: '1-5',
        [`mots-cles`]: 'fake',
      }
      const expected = {
        categories: 'Applaudir',
        date: null,
        days: '1-5',
        keywords: 'fake',
      }
      expect(windowToApiQuery(queryString)).toEqual(expected)
    })
  })
})
