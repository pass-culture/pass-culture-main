import { mount, shallow } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
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
    it('withQueryRouter gives a parse method helping for having the query params', () => {
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
      expect(query.parse()).toEqual(expectedParams)
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
      expect(query.parse()).toEqual(expectedParams)
    })

    it('withQueryRouter passes query add function that help to add value in search', () => {
      // given
      const history = createBrowserHistory()
      history.push('/test?jours=0,1&mots-cles=test')

      // when
      const wrapper = mount(
        <Router history={history}>
          <Route path="/test">
            <QueryRouterTest />
          </Route>
        </Router>
      )
      const { query } = wrapper.find('Test').props()
      query.add('jours', '2')

      // then
      const expectedParams = { jours: '0,1,2', 'mots-cles': 'test' }
      expect(query.parse()).toEqual(expectedParams)
    })

    it('withQueryRouter passes query remove function that help to remove value in search', () => {
      // given
      const history = createBrowserHistory()
      history.push('/test?jours=0,1&mots-cles=test')

      // when
      const wrapper = mount(
        <Router history={history}>
          <Route path="/test">
            <QueryRouterTest />
          </Route>
        </Router>
      )
      const { query } = wrapper.find('Test').props()
      query.remove('jours', '1')

      // then
      const expectedParams = { jours: '0', 'mots-cles': 'test' }
      expect(query.parse()).toEqual(expectedParams)
    })
  })
})
