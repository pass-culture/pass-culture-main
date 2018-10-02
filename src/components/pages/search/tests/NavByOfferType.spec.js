import configureStore from 'redux-mock-store'
import { Provider } from 'react-redux'
import React from 'react'
import { shallow } from 'enzyme'

import NavByOfferType from '../NavByOfferType'

const middlewares = []
const mockStore = configureStore(middlewares)

describe('src | components | pages | NavByOfferType', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialState = {
        data: {
          types: [
            {
              id: 0,
              sublabel: 'Regarder',
            },
            {
              id: 1,
              sublabel: 'Rencontrer',
            },
          ],
        },
      }
      const store = mockStore(initialState)
      const props = {
        pagination: {},
        title: 'fake Title',
        typeSublabels: [],
      }

      // when
      const wrapper = shallow(
        <Provider store={store}>
          <NavByOfferType {...props} />
        </Provider>
      )

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
