import verso, {
  flip,
  flipUnflippable,
  makeDraggable,
  makeUndraggable,
  unFlip,
  CLOSE_VERSO,
  MAKE_DRAGGABLE,
  MAKE_UNDRAGGABLE,
  SHOW_UNFLIPPABLE_VERSO,
  SHOW_VERSO,
} from '../verso'

describe('src | reducers | verso  ', () => {
  const state = []
  it('should return the initial state by default', () => {
    // given
    const action = {}

    // when
    const updatedState = verso(state, action)

    // then
    expect(updatedState).toEqual(state)
  })

  describe('When action.type is CLOSE_VERSO', () => {
    it('should return correct update state', () => {
      // given
      const action = { type: CLOSE_VERSO }

      // when
      const queriesReducer = verso(state, action)
      const expected = { isFlipped: false }

      // then
      expect(queriesReducer).toEqual(expected)
    })
  })

  describe('When action.type is SHOW_VERSO', () => {
    it('should return correct update state', () => {
      // given
      const action = { type: SHOW_VERSO }

      // when
      const queriesReducer = verso(state, action)
      const expected = { isFlipped: true }

      // then
      expect(queriesReducer).toEqual(expected)
    })
  })

  describe('When action.type is MAKE_UNDRAGGABLE', () => {
    it('should return correct update state', () => {
      // given
      const action = { type: MAKE_UNDRAGGABLE }

      // when
      const queriesReducer = verso(state, action)
      const expected = { draggable: false }

      // then
      expect(queriesReducer).toEqual(expected)
    })
  })

  describe('When action.type is MAKE_DRAGGABLE', () => {
    it('should return correct update state', () => {
      // given
      const action = { type: MAKE_DRAGGABLE }

      // when
      const queriesReducer = verso(state, action)
      const expected = { draggable: true }

      // then
      expect(queriesReducer).toEqual(expected)
    })
  })

  describe('When action.type is SHOW_UNFLIPPABLE_VERSO', () => {
    it('should return correct update state', () => {
      // given
      const action = {
        type: SHOW_UNFLIPPABLE_VERSO,
      }

      // when
      const queriesReducer = verso(state, action)
      const expected = {
        isFlipped: true,
        unFlippable: true,
      }

      // then
      expect(queriesReducer).toEqual(expected)
    })
  })

  describe('src | actions', () => {
    describe('flip', () => {
      it('should return correct action type', () => {
        // when
        const action = flip({})
        const expected = {
          type: SHOW_VERSO,
        }

        // then
        expect(action).toMatchObject(expected)
      })
    })
    describe('flipUnflippable', () => {
      it('should return correct action type', () => {
        // when
        const action = flipUnflippable({})
        const expected = {
          type: SHOW_UNFLIPPABLE_VERSO,
        }

        // then
        expect(action).toMatchObject(expected)
      })
    })

    describe('makeDraggable', () => {
      it('should return correct action type', () => {
        // when
        const action = makeDraggable({})
        const expected = {
          type: MAKE_DRAGGABLE,
        }

        // then
        expect(action).toMatchObject(expected)
      })
    })

    describe('makeUndraggable', () => {
      it('should return correct action type', () => {
        // when
        const action = makeUndraggable({})
        const expected = {
          type: MAKE_UNDRAGGABLE,
        }

        // then
        expect(action).toMatchObject(expected)
      })
    })

    describe('unFlip', () => {
      it('should return correct action type', () => {
        // when
        const action = unFlip({})
        const expected = {
          type: CLOSE_VERSO,
        }

        // then
        expect(action).toMatchObject(expected)
      })
    })
  })
})
