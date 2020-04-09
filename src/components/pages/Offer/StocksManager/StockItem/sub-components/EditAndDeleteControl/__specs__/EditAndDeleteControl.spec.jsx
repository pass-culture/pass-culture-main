import { mount, render, shallow } from 'enzyme'
import React from 'react'

import { requestData } from 'redux-saga-data'
import EditAndDeleteControl from '../EditAndDeleteControl'
import { BrowserRouter } from 'react-router-dom'
import { shape } from 'prop-types'

jest.mock('redux-saga-data', () => ({
  requestData: jest.fn(),
}))

describe('src | components | pages | Offer | StockManager | StockItem | sub-components | EditAndDeleteControl', () => {
  let props
  const router = {
    history: new BrowserRouter().history,
    route: {
      location: {},
      match: {},
    },
  }

  const createContext = () => ({
    context: { router },
    childContextTypes: { router: shape({}) },
  })

  beforeEach(() => {
    props = {
      deleteStock: jest.fn(),
      handleSetErrors: jest.fn(),
      formInitialValues: {
        id: 'EA',
      },
      stock: {
        id: 'EA',
      },
      query: {},
      isEvent: true,
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = mount(
      <tr>
        <EditAndDeleteControl {...props} />
      </tr>,
      createContext()
    )

    // then
    expect(wrapper.html()).toMatchSnapshot()
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
        const wrapper = render(<EditAndDeleteControl {...props} />, createContext())

        // then
        expect(wrapper.find('button.edit-stock').prop('disabled')).toBe(false)
        expect(wrapper.find('button.edit-stock').prop('title')).toBe('')
      })

      it('should show delete button enabled with no title', () => {
        // given
        props.isEvent = false
        props.stock.isEventDeletable = true

        // when
        const wrapper = render(<EditAndDeleteControl {...props} />, createContext())

        // then
        expect(wrapper.find('button.delete-stock').prop('disabled')).toBe(false)
        expect(wrapper.find('button.delete-stock').prop('title')).toBe('')
      })
    })

    describe('an event', () => {
      it('should show edit button enabled with no title for a future event', () => {
        // given
        props.isEvent = true
        props.stock.isEventExpired = false

        // when
        const wrapper = render(<EditAndDeleteControl {...props} />, createContext())

        // then
        expect(wrapper.find('button.edit-stock').prop('disabled')).toBe(false)
        expect(wrapper.find('button.edit-stock').prop('title')).toBe('')
      })

      it('should show edit button disabled with title for a past event', () => {
        // given
        props.isEvent = true
        props.stock.isEventExpired = true

        // when
        const wrapper = render(<EditAndDeleteControl {...props} />, createContext())

        // then
        expect(wrapper.find('button.edit-stock').prop('disabled')).toBe(true)
        expect(wrapper.find('button.edit-stock').prop('title')).toBe(
          'Les évènements passés ne sont pas modifiables'
        )
      })

      it('should show delete button enabled with no title for a future event', () => {
        // given
        props.isEvent = true
        props.stock.isEventDeletable = true

        // when
        const wrapper = render(<EditAndDeleteControl {...props} />, createContext())

        // then
        expect(wrapper.find('button.delete-stock').prop('disabled')).toBe(false)
        expect(wrapper.find('button.delete-stock').prop('title')).toBe('')
      })

      it('should show delete button disabled with title for a past event', () => {
        // given
        props.isEvent = true
        props.stock.isEventDeletable = false

        // when
        const wrapper = render(<EditAndDeleteControl {...props} />, createContext())

        // then
        expect(wrapper.find('button.delete-stock').prop('disabled')).toBe(true)
        expect(wrapper.find('button.delete-stock').prop('title')).toBe(
          'Les évènements terminés depuis plus de 48h ne peuvent être supprimés'
        )
      })
    })
  })
})
