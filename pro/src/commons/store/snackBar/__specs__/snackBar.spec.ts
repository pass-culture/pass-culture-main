import { SnackBarVariant } from '@/design-system/SnackBar/SnackBar'

import {
  addSnackBar,
  clearList,
  type ISnackBarItem,
  removeSnackBar,
  type SnackBarState,
  setIsStickyBarOpen,
  snackBarAdapter,
  initialState as snackBarInitialState,
  snackBarReducer,
} from '../reducer'

describe('snackBarReducer', () => {
  let initialState: SnackBarState
  beforeEach(() => {
    initialState = snackBarInitialState
  })

  describe('addSnackBar', () => {
    it('should add a snack bar when receiving it', () => {
      const snackBar = {
        description:
          'Votre structure a bien été enregistrée, elle est en cours de validation.',
        variant: SnackBarVariant.SUCCESS,
      }
      const action = addSnackBar(snackBar)

      const state = snackBarReducer(initialState, action)

      const snackBars = snackBarAdapter.getSelectors().selectAll(state.list)
      expect(snackBars).toHaveLength(1)
      expect(snackBars[0].description).toBe(snackBar.description)
      expect(snackBars[0].variant).toBe(snackBar.variant)
      expect(snackBars[0].id).toBeDefined()
      expect(snackBars[0].createdAt).toBeDefined()
    })
  })

  describe('removeSnackBar', () => {
    it('should remove a snack bar by id', () => {
      const snackBar: ISnackBarItem = {
        id: '123',
        description: 'Test message',
        variant: SnackBarVariant.SUCCESS,
        createdAt: '2025-01-01 12:00',
      }
      const stateWithSnackBar: SnackBarState = {
        ...initialState,
        list: snackBarAdapter.getInitialState(undefined, [snackBar]),
      }

      const state = snackBarReducer(stateWithSnackBar, removeSnackBar('123'))

      const snackBars = snackBarAdapter.getSelectors().selectAll(state.list)
      expect(snackBars).toHaveLength(0)
    })
  })

  describe('clearList', () => {
    it('should clear all snack bars', () => {
      const snackBarItems: ISnackBarItem[] = [
        {
          id: '1',
          description: 'First message',
          variant: SnackBarVariant.SUCCESS,
          createdAt: '2025-01-01 12:00',
        },
        {
          id: '2',
          description: 'Second message',
          variant: SnackBarVariant.ERROR,
          createdAt: '2025-01-01 12:01',
        },
      ]
      const stateWithSnackBars: SnackBarState = {
        ...initialState,
        list: snackBarAdapter.getInitialState(undefined, snackBarItems),
      }

      const state = snackBarReducer(stateWithSnackBars, clearList())

      const snackBars = snackBarAdapter.getSelectors().selectAll(state.list)
      expect(snackBars).toHaveLength(0)
    })
  })

  describe('setIsStickyBarOpen', () => {
    it('should set isStickyBarOpen to true', () => {
      const state = snackBarReducer(initialState, setIsStickyBarOpen(true))

      expect(state.isStickyBarOpen).toBe(true)
    })

    it('should set isStickyBarOpen to false', () => {
      const stateWithStickyBarOpen: SnackBarState = {
        ...initialState,
        isStickyBarOpen: true,
      }

      const state = snackBarReducer(
        stateWithStickyBarOpen,
        setIsStickyBarOpen(false)
      )

      expect(state.isStickyBarOpen).toBe(false)
    })
  })
})
