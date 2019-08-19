import favorites, { toggleFavoritesEditMode } from '../favorites'

describe('src | reducers | favorites', () => {
  it('should return the default state', () => {
    // given
    const state = {
      edit: false,
      data: [],
    }
    const action = {}

    // when
    const updatedFavorites = favorites(state, action)

    // then
    expect(updatedFavorites).toStrictEqual({
      edit: false,
      data: [],
    })
  })

  describe('when my action is edit', () => {
    it('should return the state with edit equal to true', () => {
      // given
      const state = {
        edit: false,
        data: [],
      }
      const action = {
        type: 'FAVORITES_EDIT_MODE',
      }

      // when
      const updatedFavorites = favorites(state, action)

      // then
      expect(updatedFavorites).toStrictEqual({
        edit: true,
        data: [],
      })
    })
  })

  describe('when my action is done', () => {
    it('should return the state with edit equal to false', () => {
      // given
      const state = {
        edit: true,
        data: [],
      }
      const action = {
        type: 'FAVORITES_EDIT_MODE',
      }

      // when
      const updatedFavorites = favorites(state, action)

      // then
      expect(updatedFavorites).toStrictEqual({
        edit: false,
        data: [],
      })
    })
  })

  it('should return the favorites edit mode type', () => {
    // when
    const editMode = toggleFavoritesEditMode()

    // then
    expect(editMode).toStrictEqual({
      type: 'FAVORITES_EDIT_MODE',
    })
  })
})
