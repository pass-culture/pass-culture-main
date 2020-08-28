import selectEntitiesByKeyAndJoin from '../selectEntitiesByKeyAndJoin'

describe('selectEntitiesByKeyAndJoin', () => {
  describe('when datum is not here', () => {
    it('should return empty list', () => {
      // given
      const state = {
        data: {
          bars: [],
          foos: [],
        },
      }

      //  when
      const result = selectEntitiesByKeyAndJoin(state, 'foos', {
        key: 'barId',
        value: 'CG',
      })

      // then
      expect(result).toStrictEqual([])
    })
  })

  describe('when datum is here', () => {
    it('should return the datum for one item in join', () => {
      // given
      const selectedFoos = [
        {
          barId: 'CG',
          id: 'AE',
        },
        {
          barId: 'CG',
          id: 'BF',
        },
      ]
      const state = {
        data: {
          bars: [{ id: 'CG' }],
          foos: [
            ...selectedFoos,
            {
              id: 'JK',
            },
          ],
        },
      }

      // when
      const result = selectEntitiesByKeyAndJoin(state, 'foos', {
        key: 'barId',
        value: 'CG',
      })

      // then
      expect(result).toStrictEqual(selectedFoos)
    })

    it('should return the datum for two items in join', () => {
      // given
      const selectedFoos = [
        {
          barId: 'CG',
          id: 'AE',
          isActive: true,
        },
        {
          barId: 'CG',
          id: 'BF',
          isActive: true,
        },
      ]
      const state = {
        data: {
          bars: [{ id: 'CG' }],
          foos: [
            ...selectedFoos,
            {
              id: 'JK',
            },
          ],
        },
      }

      // when
      const result = selectEntitiesByKeyAndJoin(state, 'foos', {
        key: 'barId',
        value: 'CG',
      })

      // then
      expect(result).toStrictEqual(selectedFoos)
    })

    it('should return the datum for two items in nested join', () => {
      // given
      const selectedFoos = [
        {
          patch: { barId: 'CG' },
          id: 'AE',
          isActive: true,
        },
        {
          patch: { barId: 'CG' },
          id: 'BF',
          isActive: true,
        },
      ]
      const state = {
        data: {
          bars: [{ id: 'CG' }],
          foos: [
            ...selectedFoos,
            {
              id: 'JK',
            },
          ],
        },
      }

      // when
      const result = selectEntitiesByKeyAndJoin(state, 'foos', {
        key: ['patch', 'barId'],
        value: 'CG',
      })

      // then
      expect(result).toStrictEqual(selectedFoos)
    })
  })
})
