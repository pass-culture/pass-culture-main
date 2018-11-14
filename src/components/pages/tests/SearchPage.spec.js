import configureStore from 'redux-mock-store'
import { Provider } from 'react-redux'
import React from 'react'
import { shallow } from 'enzyme'

import REDUX_STATE from '../../../mocks/reduxState'

import SearchPage from '../SearchPage'

const middlewares = []
const mockStore = configureStore(middlewares)

describe('src | components | pages | SearchPage', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialState = REDUX_STATE
      const store = mockStore(initialState)

      // when
      const wrapper = shallow(
        <Provider store={store}>
          <SearchPage />
        </Provider>
      )

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
  describe('mapStateToProps', () => {
    it('should update props values', () => {
      // given
      const initialState = REDUX_STATE

      const store = mockStore(initialState)

      const wrapper = shallow(<SearchPage store={store} />)

      console.log('wrapper.props().children()', wrapper.props().children())
      // FIXME
      // export mapStateToProps
      // problem with withRouter
      // search for SearchPageContent props .dive() inside wrapper doesn't work
      // put a spy on mapStateToProps
    })
  })
})
