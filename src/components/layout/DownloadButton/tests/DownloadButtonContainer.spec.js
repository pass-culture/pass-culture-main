import { mount } from 'enzyme'
import React from 'react'
import { Provider } from 'react-redux'

import { configureStore } from 'utils/store'

import DownloadButtonContainer from '../DownloadButtonContainer'

global.fetch = url => {
  if (url.includes('reimbursements/csv')) {
    const response = new Response(JSON.stringify({ foo: 'foo' }))
    return response
  }
}

window.URL = { createObjectURL: jest.fn() }

describe('src | components | Layout | DownloadButtonContainer', () => {
  it('should download data', () => {
    // given
    const props = {
      href: 'https://foo.com/reimbursements/csv',
    }
    const { store } = configureStore()

    // when
    const wrapper = mount(
      <Provider store={store}>
        <DownloadButtonContainer {...props} />
      </Provider>
    )

    // then
    wrapper.find('button').simulate('click')
    expect(window.URL.createObjectURL).toHaveBeenCalledWith()
  })
})
