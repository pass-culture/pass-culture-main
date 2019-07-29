import { mapStateToProps } from '../LostPasswordContainer'

describe('src | components | pages | LostPassword', () => {
  let props
  let state

  beforeEach(() => {
    props = {
      location: {
        search: '?change=1&token=ABC'
      }
    }
    state = {
      errors: {
        user: null
      }
    }
  })

  describe('mapStateToProps', () => {
    it('should return an object of props', () => {
      // when
      const result = mapStateToProps(state, props)

      // then
      expect(result).toStrictEqual({
        "change": "1",
        "envoye": undefined,
        "errors": [],
        "token": 'ABC'
      })
    })
  })
})
