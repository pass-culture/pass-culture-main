import favorites, { handleToggleFavorite, toggleFavoritesEditMode } from '../favorites'

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

  describe('toggle edit mode', () => {
    describe('when I want to edit', () => {
      it('should return the state with "edit" equal to true', () => {
        // given
        const state = {
          edit: false,
          data: [],
        }
        const action = {
          type: 'FAVORITES_TOGGLE_EDIT_MODE',
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
      it('should return the state with "edit" equal to false', () => {
        // given
        const state = {
          edit: true,
          data: [],
        }
        const action = {
          type: 'FAVORITES_TOGGLE_EDIT_MODE',
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
        type: 'FAVORITES_TOGGLE_EDIT_MODE',
      })
    })
  })

  describe('toggle update', () => {
    describe('when add a favorite whose does not exist', () => {
      it('should return data with this favorite', () => {
        // given
        const state = {
          edit: true,
          data: [],
        }
        const action = {
          offerId: 'MEFA',
          type: 'FAVORITES_TOGGLE_UPDATE',
        }

        // when
        const updatedFavorites = favorites(state, action)

        // then
        expect(updatedFavorites).toStrictEqual({
          edit: true,
          data: ['MEFA'],
        })
      })
    })

    describe('when add a favorite whose exists', () => {
      it('should return data without this favorite', () => {
        // given
        const state = {
          edit: true,
          data: ['o1', 'MEFA'],
        }
        const action = {
          offerId: 'MEFA',
          type: 'FAVORITES_TOGGLE_UPDATE',
        }

        // when
        const updatedFavorites = favorites(state, action)

        // then
        expect(updatedFavorites).toStrictEqual({
          edit: true,
          data: ['o1'],
        })
      })
    })

    it('should return the favorites toggle type', () => {
      // given
      const offerId = 'MEFA'

      // when
      const toggleFavorite = handleToggleFavorite(offerId)

      // then
      expect(toggleFavorite).toStrictEqual({
        offerId: 'MEFA',
        type: 'FAVORITES_TOGGLE_UPDATE',
      })
    })
  })
})
