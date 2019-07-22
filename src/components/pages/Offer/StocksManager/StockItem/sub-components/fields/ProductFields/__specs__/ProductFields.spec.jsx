import { createBrowserHistory } from 'history'
import React from 'react'
import { mount, shallow } from 'enzyme'
import { Field } from 'pass-culture-shared'
import configureStore from 'redux-mock-store'
import { Provider } from 'react-redux'
import { Route, Router } from 'react-router-dom'

import ProductFields from '../ProductFields'
import state from '../../../../../../../../utils/mocks/state'
const middlewares = []
const mockStore = configureStore(middlewares)
const dispatchMock = jest.fn()
const closeInfoMock = jest.fn()
const showInfoMock = jest.fn()

describe('src | components | pages | Offer | StocksManager | StockItem | sub-components | fields | ProductFields', () => {
  it('should match the snapshot', () => {
    // given
    const initialProps = {
      closeInfo: jest.fn(),
      dispatch: jest.fn(),
      hasIban: false,
      parseFormChild: jest.fn(),
      showInfo: jest.fn(),
      venue: {},
    }

    // when
    const wrapper = shallow(<ProductFields {...initialProps} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })
})
