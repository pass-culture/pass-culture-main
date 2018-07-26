import user, {
  setUser,
  SET_USER
} from '../user'

describe('src | reducers | user  ', () => {
  const state = []

  const fakeUser =
    {
      canBook: false,
      dateCreated: '2018-07-20T08:48:57.952778Z',
      dehumanizedId: 3,
      departementCode: '93',
      email: 'pctest.cafe@btmx.fr',
      firstThumbDominantColor: [
        62,
        54,
        51
      ],
      id: 'FT',
      isAdmin: false,
      modelName: 'User',
      publicName: 'Utilisateur test',
      thumbCount: 1
    }
    
    it('should return the initial state by default', () => {
      // given
      const action = {}

      // when
      const updatedState = user(state, action)

      // then
      expect(updatedState).toEqual(state)
    })

    it('should return the result', () => {
      // given
      const action = {
        type: SET_USER,
        user: fakeUser
      }

      // when
      const result = user(state, action)

      // then
      expect(result).toEqual(fakeUser)
    })

    describe('src | actions', () => {
      describe('setUser', () => {
        it('should return correct action', () => {
          // given


          // when
          const action = setUser(fakeUser)
          const expected = {
            type: SET_USER,
            user: fakeUser,
          }

          // then
          expect(action).toMatchObject(expected)
        })
      })
    })
})
