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
    describe('withQueryRouter passes pagination query object that has parsed location search', () => {
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
      const query = wrapper.find('Test').props().pagination.query
      const expectedQuery = {
        query: { 'mots-cles': 'test', page: '1' },
      }
      expect(query).toEqual(expectedQuery)
    })

    describe('withQueryRouter passes pagination change function that help to modify location search', () => {
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
      const pagination = wrapper.find('Test').props().pagination.query
      const expectedQuery = {
        query: { 'mots-cles': 'test', page: '1' },
      }
      expect(testedQuery).toEqual(expectedQuery)
    })
  })
})
