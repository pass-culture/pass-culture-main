import selectOfferers from '../selectOfferers'

describe('src | selectors | selectOfferers', () => {
  describe('when the offerers key is missing', () => {
    it('should return an empty array', () => {
      // given
      const state = {
        data: {},
      }

      // when
      const result = selectOfferers(state)

      // then
      expect(result).toStrictEqual([])
    })
  })

  it('should return the list of offerers from the state', () => {
    // given
    const state = {
      data: {
        offerers: [
          {
            id: 'M4',
            isValidated: true,
          },
          {
            id: 'NE',
            isValidated: false,
          },
        ],
      },
    }

    // when
    const result = selectOfferers(state)

    // then
    expect(result).toStrictEqual([
      {
        id: 'M4',
        isValidated: true,
      },
      {
        id: 'NE',
        isValidated: false,
      },
    ])
  })
})
