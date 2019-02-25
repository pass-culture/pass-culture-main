import React from 'react'
import { shallow } from 'enzyme'
import RawOfferItem from '../RawOfferItem'
import mockedOffers from './offersMock'

import configureStore from 'redux-mock-store'
import { Provider } from 'react-redux'

const middlewares = []
const mockStore = configureStore(middlewares)

describe('snapshot', () => {
  it('should match snapshot', () => {
    // given
    const initialState = {}
    const store = mockStore(initialState)
    const dispatchMock = jest.fn()
    const initialProps = {
      dispatch: dispatchMock,
      offer: mockedOffers[0],
      location: {
        search: '?orderBy=offer.id+desc',
      },
    }

    // when
    const wrapper = shallow(
      <Provider store={store}>
        <RawOfferItem {...initialProps} />
      </Provider>
    )

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
    dispatchMock.mockClear()
  })
})
