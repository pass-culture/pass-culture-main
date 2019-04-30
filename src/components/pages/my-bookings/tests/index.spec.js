import React from 'react'
import { mount } from 'enzyme'
import { requestData } from 'redux-saga-data'
import { MemoryRouter } from 'react-router-dom'

import { RawMyBookingsPage } from '../index'

jest.mock('redux-saga-data', () => ({
  requestData: jest.fn(),
}))

describe('src | components | pages | my-bookings | RawMyBookingsPage', () => {
  it('must check that requestData is been called with a stateKey equal to bookings', () => {
    // given
    const props = {
      dispatch: jest.fn(),
      otherBookings: [],
      soonBookings: [],
    }

    // when
    const wrapper = mount(
      <MemoryRouter>
        <RawMyBookingsPage {...props} />
      </MemoryRouter>
    )
    // const nestedComponent = wrapper.find(RawMyBookingsPage)
    // nestedComponent.instance().handleRequestFail = mockHandleFail
    // nestedComponent.instance().handleRequestSuccess = mockHandleSuccess

    // then
    expect(wrapper).toBeDefined()
    expect(requestData).toHaveBeenCalledWith({
      apiPath: '/bookings',
      handleFail: expect.any(Function),
      handleSuccess: expect.any(Function),
      normalizer: { recommendation: 'recommendations' },
      stateKey: 'bookings',
    })
  })
})
