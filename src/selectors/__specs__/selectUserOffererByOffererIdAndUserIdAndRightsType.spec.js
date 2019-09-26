import selectUserOffererByOffererIdAndUserIdAndRightsType from '../selectUserOffererByOffererIdAndUserIdAndRightsType'

describe('src | selectors | selectUserOffererByOffererIdAndUserIdAndRightsType', () => {
  it('should return an array of object when state contains user offerer with asked rights', () => {
    // given
    const state = {
      data: {
        userOfferers: [
          {
            id: 'AEKQ',
            modelName: 'UserOfferer',
            offererId: 'FQ',
            rights: 'admin',
            userId: 'NU',
          },
        ],
      },
    }
    const offererId = 'FQ'
    const currentUserId = 'NU'

    // when
    const result = selectUserOffererByOffererIdAndUserIdAndRightsType(
      state,
      offererId,
      currentUserId,
      'admin'
    )

    // then
    const expected = {
      id: 'AEKQ',
      modelName: 'UserOfferer',
      offererId: 'FQ',
      rights: 'admin',
      userId: 'NU',
    }
    expect(result).toStrictEqual(expected)
  })
})
