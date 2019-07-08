import React from 'react'
import { shallow } from 'enzyme'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'

import OfferItem from '../OfferItem'
import mockedOffers from '../../tests/offersMock'

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
        <OfferItem {...initialProps} />
      </Provider>
    )

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
    dispatchMock.mockClear()
  })
})
