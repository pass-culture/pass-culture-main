import { mount } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider, connect } from 'react-redux'
import { Route, Router, Switch } from 'react-router-dom'
import { compose } from 'redux'

import Venue from '../Venue'
import mapDispatchToProps from '../mapDispatchToProps'
import mapStateToProps from '../mapStateToProps'
import { withFrenchQueryRouter } from '../../../../components/hocs'
import { venueNormalizer } from '../../../../utils/normalizers'
import { configureStore } from '../../../../utils/store'

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

window.scroll = () => {}

const ADDRESS = "5 cité de l'enfer"
const CITY = 'Paboude'
const LATITUDE = 48.3
const LONGITUDE = 1.2
const MANAGING_OFFERER_ID = 'AE'
const NAME = 'foo'
const POSTAL_CODE = '75010'
const SIRET = '12345678912345'
const mockSuccessSiretInfo = {
  etablissement: {
    code_postal: POSTAL_CODE,
    l1_normalisee: NAME,
    l4_normalisee: ADDRESS,
    libelle_commune: CITY,
    latitude: LATITUDE,
    longitude: LONGITUDE,
    siret: SIRET,
  },
}

global.fetch = url => {
  if (url.includes(SIRET)) {
    const response = new Response(JSON.stringify(mockSuccessSiretInfo))
    return response
  }
  return new Response(JSON.stringify({}))
}

const VenueContainer = compose(
  withFrenchQueryRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(Venue)

describe('src | components | pages | Venue', () => {
  it('fill the form with a valid siret', done => {
    // given
    const { store } = configureStore()
    const history = createBrowserHistory()
    history.push(`/structures/${MANAGING_OFFERER_ID}/lieux/creation`)
    const values = {
      address: ADDRESS,
      bookingEmail: 'fifi@moc.com',
      city: CITY,
      latitude: LATITUDE,
      longitude: LONGITUDE,
      managingOffererId: MANAGING_OFFERER_ID,
      name: NAME,
      postalCode: POSTAL_CODE,
      siret: SIRET,
    }
    const wrapper = mount(
      <Provider store={store}>
        <Router history={history}>
          <Switch>
            <Route path="/structures/:offererId/lieux/:venueId">
              <VenueContainer />
            </Route>
          </Switch>
        </Router>
      </Provider>
    )
    wrapper
      .find("input[name='bookingEmail']")
      .simulate('change', { target: { value: values.bookingEmail } })
    wrapper
      .find("input[name='siret']")
      .simulate('change', { target: { value: values.siret } })

    // then
    setTimeout(() => {
      // when
      wrapper.update()
      const submitButton = wrapper.find('button[type="submit"]')
      expect(submitButton.props().disabled).toEqual(false)

      // when
      submitButton.simulate('submit')

      // then
      const expectedSubConfig = {
        apiPath: '/venues/',
        body: values,
        method: 'POST',
        normalizer: venueNormalizer,
      }
      const receivedConfig = mockRequestDataCatch.mock.calls.slice(-1)[0][0]
      Object.keys(expectedSubConfig).forEach(key =>
        expect(receivedConfig[key]).toEqual(expectedSubConfig[key])
      )

      // done
      done()
    })
  })
})
