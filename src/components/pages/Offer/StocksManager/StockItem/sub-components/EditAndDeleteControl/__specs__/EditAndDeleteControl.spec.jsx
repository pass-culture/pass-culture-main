import { render, shallow } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router'
import { requestData } from 'redux-saga-data'

import configureStore from '../../../../../../../../utils/store'
import EditAndDeleteControl from '../EditAndDeleteControl'

jest.mock('redux-saga-data', () => {
  const actualModule = jest.requireActual('redux-saga-data')

  return {
    ...actualModule,
    requestData: jest.fn(),
  }
})

describe('src | components | pages | Offer | StockManager | StockItem | sub-components | EditAndDeleteControl', () => {
  let props
  let history
  let store

  beforeEach(() => {
    props = {
      deleteStock: jest.fn(),
      handleSetErrors: jest.fn(),
      formInitialValues: {
        id: 'EA',
      },
      stock: {
        id: 'EA',
        isEventDeletable: true,
        isEventExpired: false,
      },
      query: {},
      isEvent: true,
    }
    history = createBrowserHistory()
    store = configureStore().store
  })

  describe('handleOnConfirmDeleteClick()', () => {
    it('should dispatch the request data', () => {
      // given
      const expectedAction = {
        type: '/stocks/ID',
      }
      requestData.mockReturnValue(expectedAction)
      const wrapper = shallow(<EditAndDeleteControl.WrappedComponent {...props} />)

      // when
      wrapper.instance().handleOnConfirmDeleteClick()

      // then
      expect(props.deleteStock).toHaveBeenCalledWith(
        props.formInitialValues.id,
        expect.any(Function)
      )
    })
  })

  describe('render()', () => {
    describe('a thing', () => {
      it('should show edit button enabled with no title', () => {
        // given
        props.isEvent = false

        // when
        const wrapper = render(
          <Router history={history}>
            <Provider store={store}>
              <EditAndDeleteControl {...props} />
            </Provider>
          </Router>
        )

        // then
        const editButton = wrapper.find('[alt="Modifier"]').parents('button')
        expect(editButton.prop('disabled')).toBe(false)
        expect(editButton.prop('title')).toBe('')
      })

      it('should show delete button enabled with no title', () => {
        // given
        props.isEvent = false
        props.stock.isEventDeletable = true

        // when
        const wrapper = render(
          <Router history={history}>
            <Provider store={store}>
              <EditAndDeleteControl {...props} />
            </Provider>
          </Router>
        )

        // then
        const deleteButton = wrapper.find('[alt="Supprimer"]').parents('button')
        expect(deleteButton.prop('disabled')).toBe(false)
        expect(deleteButton.prop('title')).toBe('')
      })
    })

    describe('an event', () => {
      it('should show edit button enabled with no title for a future event', () => {
        // given
        props.isEvent = true
        props.stock.isEventExpired = false

        // when
        const wrapper = render(
          <Router history={history}>
            <Provider store={store}>
              <EditAndDeleteControl {...props} />
            </Provider>
          </Router>
        )

        // then
        const editButton = wrapper.find('[alt="Modifier"]').parents('button')
        expect(editButton.prop('disabled')).toBe(false)
        expect(editButton.prop('title')).toBe('')
      })

      it('should show edit button disabled with title for a past event', () => {
        // given
        props.isEvent = true
        props.stock.isEventExpired = true

        // when
        const wrapper = render(
          <Router history={history}>
            <Provider store={store}>
              <EditAndDeleteControl {...props} />
            </Provider>
          </Router>
        )

        // then
        const editButton = wrapper.find('[alt="Modifier"]').parents('button')
        expect(editButton.prop('disabled')).toBe(true)
        expect(editButton.prop('title')).toBe('Les évènements passés ne sont pas modifiables')
      })

      it('should show delete button enabled with no title for a future event', () => {
        // given
        props.isEvent = true
        props.stock.isEventDeletable = true

        // when
        const wrapper = render(
          <Router history={history}>
            <Provider store={store}>
              <EditAndDeleteControl {...props} />
            </Provider>
          </Router>
        )

        // then
        const deleteButton = wrapper.find('[alt="Supprimer"]').parents('button')
        expect(deleteButton.prop('disabled')).toBe(false)
        expect(deleteButton.prop('title')).toBe('')
      })

      it('should show delete button disabled with title for a past event', () => {
        // given
        props.isEvent = true
        props.stock.isEventDeletable = false

        // when
        const wrapper = render(
          <Router history={history}>
            <Provider store={store}>
              <EditAndDeleteControl {...props} />
            </Provider>
          </Router>
        )

        // then
        const deleteButton = wrapper.find('[alt="Supprimer"]').parents('button')
        expect(deleteButton.prop('disabled')).toBe(true)
        expect(deleteButton.prop('title')).toBe(
          'Les évènements terminés depuis plus de 48 heures ne peuvent être supprimés'
        )
      })
    })
  })
})
