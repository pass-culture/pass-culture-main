import { shallow } from 'enzyme'
import React from 'react'
import configureStore from 'redux-mock-store'
import { Provider } from 'react-redux'

import { requestData } from 'redux-saga-data'
import EditAndDeleteControl from '../EditAndDeleteControl'

const middlewares = []
const mockStore = configureStore(middlewares)

jest.mock('redux-saga-data', () => ({
  requestData: jest.fn(),
}))

describe('src | components | pages | Offer | StockManager | StockItem | sub-components | EditAndDeleteControl', () => {
  let props

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
    // given
    const initialState = {}
    const store = mockStore(initialState)

    // when
    const wrapper = shallow(
      <Provider store={store}>
        <EditAndDeleteControl {...props} />
      </Provider>
    )

    // then
    expect(wrapper).toMatchSnapshot()
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
})
