import { mount, shallow } from 'enzyme'
import React from 'react'
import { createBrowserHistory } from 'history'
import { Route, Router } from 'react-router-dom'

import { withQueryRouter } from '../withQueryRouter'

const Test = () => null
const QueryRouterTest = withQueryRouter(Test)

describe('src | components | pages | hocs | withQueryRouter', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<QueryRouterTest />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
  describe('functions ', () => {
    it('withQueryRouter passes pagination query object that has parsed location search', () => {
      // given
      const history = createBrowserHistory()
      history.push('/test?page=1&mots-cles=test')

      // when
      const wrapper = mount(
        <Router history={history}>
          <Route path="/test">
            <QueryRouterTest />
          </Route>
        </Router>
      )

      // then
      const { query } = wrapper.find('Test').props()
      const expectedParams = { 'mots-cles': 'test', page: '1' }
      expect(query.params).toEqual(expectedParams)
    })

    it('withQueryRouter passes query change function that help to modify location search', () => {
      // given
      const history = createBrowserHistory()
      history.push('/test?page=1&mots-cles=test')

      // when
      const wrapper = mount(
        <Router history={history}>
          <Route path="/test">
            <QueryRouterTest />
          </Route>
        </Router>
      )
      const { query } = wrapper.find('Test').props()
      query.change({ 'mots-cles': null, page: 2 })

      // then
      const expectedParams = { page: '2' }
      expect(query.params).toEqual(expectedParams)
    })
  })
})
