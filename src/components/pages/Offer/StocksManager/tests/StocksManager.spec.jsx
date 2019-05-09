<<<<<<< HEAD
import React from 'react'
import { shallow } from 'enzyme'

import StocksManager from '../StocksManager'

const mockedStock = {
  available: 10,
  bookingLimitDatetime: '2019-03-06T23:00:00Z',
  bookingRecapSent: null,
  dateModified: '2019-03-06T15:51:39.253527Z',
  dateModifiedAtLastProvider: '2019-03-06T15:51:39.253504Z',
  eventOccurrenceId: null,
  groupSize: 1,
  id: 'ARMQ',
  idAtProviders: null,
  isSoftDeleted: false,
  lastProviderId: null,
  modelName: 'Stock',
  offerId: 'AUSQ',
  price: 17,
}

describe('src | components | pages | Offer | StocksManager', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialProps = {
        location: {
          pathname: '/offres/AWHA',
          search: '?gestion',
          hash: '',
          state: undefined,
          key: '4c2v7m',
        },
        query: { context: () => ({}) },
        stocks: [mockedStock],
      }

      // when
      const wrapper = shallow(<StocksManager {...initialProps} />)
=======
import { mount, shallow } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider, connect } from 'react-redux'
import { Route, Router, Switch } from 'react-router-dom'
import { compose } from 'redux'

import StocksManager from '../StocksManager'
import mapStateToProps from '../mapStateToProps'
import { withFrenchQueryRouter } from 'components/hocs'
import { configureStore } from 'utils/store'

const mockRequestDataCatch = jest.fn()
jest.mock('redux-saga-data', () => {
  const actualModule = jest.requireActual('redux-saga-data')
  return {
    ...actualModule,
    requestData: config => {
      mockRequestDataCatch(config)
      return actualModule.requestData(config)
    },
  }
})

global.fetch = url => {
  return new Response(JSON.stringify({}))
}

const StocksManagerContainer = compose(
  withFrenchQueryRouter,
  connect(mapStateToProps)
)(StocksManager)

describe('src | components | pages | Offer | StocksManager', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<StocksManager />)
>>>>>>> (pC-1875) prepared test

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
<<<<<<< HEAD
=======

  describe('mount', () => {
    it.skip('reset the form when we click on cancel', done => {
      // given
      const { store } = configureStore()
      const history = createBrowserHistory()
      history.push(`/offres/AE?gestion`)
      const wrapper = mount(
        <Provider store={store}>
          <Router history={history}>
            <Switch>
              <Route path="/offres/:offerId">
                <StocksManagerContainer />
              </Route>
            </Switch>
          </Router>
        </Provider>
      )

      setTimeout(() => {
        // then (offerer request is done, form is now available)
        wrapper.update()

        // when
        wrapper
          .find("input[name='beginningTime']")
          .simulate('change', { target: { value: '12h13' } })

        setTimeout(() => {
          // when (siret has filled other inputs, submit button is not anymore disabled)
          wrapper.update()
          const cancelButton = wrapper.find('button.cancel-step')
          cancelButton.simulate('submit')

          // then
          /*
          wrapper
            .find("input[name='beginningTime']")
            .simulate('change', { target: { value: "12h13" } })
          */

          // done
          done()
        })
      })
    })
  })
>>>>>>> (pC-1875) prepared test
})
