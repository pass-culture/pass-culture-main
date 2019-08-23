import selectOfferers from '../selectOfferers'

describe('src | selectors | selectOfferers', () => {
  it('should return an empty array when the offerers key is missing', () => {
    // given
    const state = {
      data: {},
    }

    // when
    const result = selectOfferers(state)

    // then
    expect(result).toStrictEqual([])
  })

  it('should the list of offerers from the state', () => {
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
