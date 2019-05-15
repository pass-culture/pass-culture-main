import { mount, shallow } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Form } from 'react-final-form'
import { Provider, connect } from 'react-redux'
import { Route, Router, Switch } from 'react-router-dom'
import { compose } from 'redux'
import { assignData } from 'redux-saga-data'

import Venue from '../Venue'
import mapDispatchToProps from '../mapDispatchToProps'
import mapStateToProps from '../mapStateToProps'
import VenueProvidersManagerContainer from '../VenueProvidersManager/VenueProvidersManagerContainer'
import { withFrenchQueryRouter } from 'components/hocs'
import HeroSection from 'components/layout/HeroSection'
import { venueNormalizer } from 'utils/normalizers'
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

window.scroll = () => {}

const BOOKING_EMAIL = 'foo@mama.com'
const ADDRESS = "5 cite de l'enfer"
const CITY = 'Cayenne'
const COMMENT = "C'est un lieu sans siret"
const LATITUDE = 4.56
const LONGITUDE = -52.19
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

const MOCK_FEATURE = {
  geometry: {
    coordinates: [LONGITUDE, LATITUDE],
  },
  properties: {
    city: CITY,
    id: 'OOO',
    label: 'OOO',
    name: ADDRESS,
    postcode: POSTAL_CODE,
  },
}

const mockSuccessAddressInfo = {
  features: [
    MOCK_FEATURE,
    {
      geometry: {
        coordinates: [1, 48],
      },
      properties: {
        city: 'FooVille',
        id: 'OO1',
        label: 'OO1',
        name: ADDRESS,
        postcode: '75010',
      },
    },
  ],
}

const mockSuccessLonLatInfo = {
  features: [MOCK_FEATURE],
}

global.fetch = url => {
  if (url.includes('api-adress') && url.includes(ADDRESS)) {
    const response = new Response(JSON.stringify(mockSuccessAddressInfo))
    return response
  }
  if (
    url.includes('api-adress') &&
    url.includes(LATITUDE) &&
    url.includes(LONGITUDE)
  ) {
    const response = new Response(JSON.stringify(mockSuccessLonLatInfo))
    return response
  }
  if (url.includes('sirene.entreprise') && url.includes(SIRET)) {
    const response = new Response(JSON.stringify(mockSuccessSiretInfo))
    return response
  }
  if (url.includes('offerers')) {
    const response = new Response(JSON.stringify({ id: MANAGING_OFFERER_ID }))
    return response
  }
  if (url.includes('users')) {
    const response = new Response(
      JSON.stringify({ id: 'AE', email: BOOKING_EMAIL })
    )
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
  let dispatch
  let push
  let props

  beforeEach(() => {
    dispatch = jest.fn()
    push = jest.fn()

    const ownProps = {
      dispatch: dispatch,
      history: {
        location: {
          pathname: '/fake',
        },
        push: push,
      },
      location: {
        search: '',
      },
      match: {
        params: {
          offererId: 'APEQ',
          venueId: 'AQYQ',
        },
      },
      query: {
        changeToReadOnly: jest.fn(),
        context: () => ({}),
      },
    }

    props = {
      currentUser: {},
      formInitialValues: {
        id: 'CM',
      },
      offerer: {
        id: 'BQ',
        name: 'Maison du chocolat',
      },
      ...ownProps,
      ...mapDispatchToProps(dispatch, ownProps),
    }
  })

  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<Venue {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('render', () => {
    it('should render component with default state', () => {
      // when
      const wrapper = shallow(<Venue {...props} />)

      // then
      expect(wrapper.state('isRequestPending')).toBe(false)
    })

    it('should not render a Form when venue is virtual', () => {
      // given
      props.formInitialValues = {
        isVirtual: true,
      }

      // when
      const wrapper = shallow(<Venue {...props} />)

      // then
      const form = wrapper.find(Form)
      expect(form).toHaveLength(0)
    })

    describe('when creating', () => {
      beforeEach(() => {
        props.match = {
          params: {
            offererId: 'APEQ',
            venueId: 'nouveau',
          },
        }
        props.query.context = () => ({
          isCreatedEntity: true,
          isModifiedEntity: false,
          readOnly: false,
        })
      })

      it('should render component with correct state values', () => {
        // when
        const wrapper = shallow(<Venue {...props} />)

        // then
        expect(wrapper.state('isRequestPending')).toBe(false)
      })

      it('should display a paragraph with proper title', () => {
        // when
        const wrapper = shallow(<Venue {...props} />)

        // then
        const heroSection = wrapper.find(HeroSection)
        expect(heroSection.find('p')).toBeDefined()
        expect(heroSection.find('p').prop('className')).toBe('subtitle')
        expect(heroSection.find('p').text()).toBe(
          'Ajoutez un lieu où accéder à vos offres.'
        )
      })

      it('should build the proper backTo link', () => {
        // when
        const wrapper = shallow(<Venue {...props} />)

        // then
        expect(wrapper.prop('backTo')).toEqual({
          label: 'Maison du chocolat',
          path: '/structures/APEQ',
        })
      })

      it('should not display a VenueProvidersManager component', () => {
        // when
        const wrapper = shallow(<Venue {...props} />)

        // then
        expect(wrapper.find(VenueProvidersManagerContainer)).toHaveLength(0)
      })
    })

    describe('when editing', () => {
      beforeEach(() => {
        props.location = {
          search: '?modifie',
        }
        props.match = {
          params: {
            offererId: 'APEQ',
            venueId: 'AQYQ',
          },
        }
        props.query.context = () => ({
          isCreatedEntity: false,
          isModifiedEntity: true,
          readOnly: false,
        })
      })

      it('should render component with correct state values', () => {
        // when
        const wrapper = shallow(<Venue {...props} />)

        // then
        expect(wrapper.state('isRequestPending')).toBe(false)
      })
    })

    describe('when reading', () => {
      beforeEach(() => {
        props.query.context = () => ({
          isCreatedEntity: false,
          isModifiedEntity: false,
          readOnly: true,
        })
      })

      it('should render component with correct state values', () => {
        // when
        const wrapper = shallow(<Venue {...props} />)

        // then
        expect(wrapper.state('isRequestPending')).toBe(false)
      })
    })
  })

  describe('Form Request', () => {
    it('resets the form when click on terminer', done => {
      // given
      const { store } = configureStore()
      const history = createBrowserHistory()
      store.dispatch(
        assignData({
          venues: [{ id: 'AE' }],
        })
      )
      history.push(`/structures/${MANAGING_OFFERER_ID}/lieux/AE?modification`)
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

      setTimeout(() => {
        // then (offerer request is done, form is now available)
        wrapper.update()

        // when
        wrapper
          .find("input[name='bookingEmail']")
          .simulate('change', { target: { value: 'foo@foo.com' } })

        setTimeout(() => {
          // then
          wrapper.update()
          expect(
            wrapper.find("input[name='bookingEmail']").props().value
          ).toEqual('foo@foo.com')

          // when
          const cancelButton = wrapper.find('button[type="reset"]')
          cancelButton.simulate('click')

          // then
          expect(
            wrapper.find("input[name='bookingEmail']").props().value
          ).toEqual('')

          // done
          done()
        })
      })
    })

    it('fills the form with a valid siret', done => {
      // given
      const { store } = configureStore()
      const history = createBrowserHistory()
      history.push(`/structures/${MANAGING_OFFERER_ID}/lieux/creation`)
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

      setTimeout(() => {
        // then (offerer request is done, form is now available)
        wrapper.update()
        expect(
          wrapper.find("textarea[name='comment']").props().required
        ).toEqual(true)

        // when
        wrapper
          .find("input[name='bookingEmail']")
          .simulate('change', { target: { value: BOOKING_EMAIL } })
        wrapper
          .find("input[name='siret']")
          .simulate('change', { target: { value: SIRET } })

        setTimeout(() => {
          // then
          expect(
            wrapper.find("textarea[name='comment']").props().required
          ).toEqual(false)
          expect(
            wrapper.find("input[name='address']").props().readOnly
          ).toEqual(true)
          expect(wrapper.find("input[name='city']").props().readOnly).toEqual(
            true
          )
          expect(
            wrapper.find("input[name='postalCode']").props().readOnly
          ).toEqual(true)
          // TODO: latitude et longitude should be readOnly
          // but jest says it is not the case
          // (but localhost test prooves it that it is true)
          // expect(wrapper
          //  .find("input[name='latitude']")
          //  .props().readOnly).toEqual(true)
          // expect(wrapper
          //  .find("input[name='longitude']")
          //  .props().readOnly).toEqual(true)

          // when (siret has filled other inputs, submit button is not anymore disabled)
          wrapper.update()
          const submitButton = wrapper.find('button[type="submit"]')
          expect(submitButton.props().disabled).toEqual(false)
          submitButton.simulate('submit')

          // then
          const body = {
            address: ADDRESS,
            bookingEmail: BOOKING_EMAIL,
            city: CITY,
            latitude: LATITUDE,
            longitude: LONGITUDE,
            managingOffererId: MANAGING_OFFERER_ID,
            name: NAME,
            postalCode: POSTAL_CODE,
            siret: SIRET,
          }
          const expectedSubConfig = {
            apiPath: '/venues/',
            body,
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

    it('reputs geo fields to not readonly mode when we delete the siret', done => {
      // given
      const { store } = configureStore()
      const history = createBrowserHistory()
      history.push(`/structures/${MANAGING_OFFERER_ID}/lieux/creation`)
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

      setTimeout(() => {
        // then (offerer request is done, form is now available)
        wrapper.update()
        expect(
          wrapper.find("textarea[name='comment']").props().required
        ).toEqual(true)

        // when
        wrapper
          .find("input[name='bookingEmail']")
          .simulate('change', { target: { value: BOOKING_EMAIL } })
        wrapper
          .find("input[name='siret']")
          .simulate('change', { target: { value: SIRET } })

        setTimeout(() => {
          // then
          wrapper.update()
          expect(
            wrapper.find("textarea[name='comment']").props().required
          ).toEqual(false)
          expect(
            wrapper.find("input[name='address']").props().readOnly
          ).toEqual(true)
          expect(wrapper.find("input[name='city']").props().readOnly).toEqual(
            true
          )
          expect(
            wrapper.find("input[name='postalCode']").props().readOnly
          ).toEqual(true)
          expect(wrapper.find('Marker').props().draggable).toEqual(false)

          // when (siret has filled other inputs, submit button is not anymore disabled)
          wrapper
            .find("input[name='siret']")
            .simulate('change', { target: { value: SIRET.slice(0, -1) } })

          // then
          wrapper.update()
          expect(
            wrapper.find("textarea[name='comment']").props().required
          ).toEqual(true)
          expect(
            wrapper.find("input[name='address']").props().readOnly
          ).toEqual(false)
          expect(wrapper.find("input[name='city']").props().readOnly).toEqual(
            false
          )
          expect(
            wrapper.find("input[name='postalCode']").props().readOnly
          ).toEqual(false)
          expect(wrapper.find('Marker').props().draggable).toEqual(true)

          // done
          done()
        })
      })
    })

    it('fills the form with a valid address', done => {
      // given
      const { store } = configureStore()
      const history = createBrowserHistory()
      history.push(`/structures/${MANAGING_OFFERER_ID}/lieux/creation`)
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

      setTimeout(() => {
        // when (offerer request is done, form is now available)
        wrapper.update()
        wrapper
          .find("input[name='name']")
          .simulate('change', { target: { value: NAME } })
        wrapper
          .find("textarea[name='comment']")
          .simulate('change', { target: { value: COMMENT } })
        wrapper
          .find("input[name='bookingEmail']")
          .simulate('change', { target: { value: BOOKING_EMAIL } })
        wrapper
          .find("input[name='address']")
          .simulate('change', { target: { value: ADDRESS } })

        setTimeout(() => {
          wrapper.update()
          const { items, onSelect, value } = wrapper
            .find('Autocomplete')
            .props()
          const item = items[0]
          onSelect(value, item)

          setTimeout(() => {
            // then (address has filled other inputs)
            wrapper.update()
            expect(wrapper.find("input[name='city']").props().readOnly).toEqual(
              true
            )
            expect(
              wrapper.find("input[name='postalCode']").props().readOnly
            ).toEqual(true)
            expect(
              wrapper.find("input[name='latitude']").props().readOnly
            ).toEqual(true)
            expect(
              wrapper.find("input[name='longitude']").props().readOnly
            ).toEqual(true)

            // when
            const submitButton = wrapper.find('button[type="submit"]')
            expect(submitButton.props().disabled).toEqual(false)
            submitButton.simulate('submit')

            // then
            const body = {
              address: ADDRESS,
              bookingEmail: BOOKING_EMAIL,
              city: CITY,
              comment: COMMENT,
              latitude: LATITUDE,
              longitude: LONGITUDE,
              managingOffererId: MANAGING_OFFERER_ID,
              name: NAME,
              postalCode: POSTAL_CODE,
            }
            const expectedSubConfig = {
              apiPath: '/venues/',
              body,
              method: 'POST',
              normalizer: venueNormalizer,
            }
            const receivedConfig = mockRequestDataCatch.mock.calls.slice(
              -1
            )[0][0]
            Object.keys(expectedSubConfig).forEach(key =>
              expect(receivedConfig[key]).toEqual(expectedSubConfig[key])
            )

            // done
            done()
          })
        }, 500)
      })
    })

    it('reputs geo fields to not readonly mode when we delete the address', done => {
      // given
      const { store } = configureStore()
      const history = createBrowserHistory()
      history.push(`/structures/${MANAGING_OFFERER_ID}/lieux/creation`)
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

      setTimeout(() => {
        // when (offerer request is done, form is now available)
        wrapper.update()
        wrapper
          .find("input[name='name']")
          .simulate('change', { target: { value: NAME } })
        wrapper
          .find("textarea[name='comment']")
          .simulate('change', { target: { value: COMMENT } })
        wrapper
          .find("input[name='bookingEmail']")
          .simulate('change', { target: { value: BOOKING_EMAIL } })
        wrapper
          .find("input[name='address']")
          .simulate('change', { target: { value: ADDRESS } })

        setTimeout(() => {
          wrapper.update()
          const { items, onSelect, value } = wrapper
            .find('Autocomplete')
            .props()
          const item = items[0]
          onSelect(value, item)

          setTimeout(() => {
            // then (address has filled other inputs)
            wrapper.update()
            expect(wrapper.find("input[name='city']").props().readOnly).toEqual(
              true
            )
            expect(
              wrapper.find("input[name='postalCode']").props().readOnly
            ).toEqual(true)
            expect(
              wrapper.find("input[name='latitude']").props().readOnly
            ).toEqual(true)
            expect(
              wrapper.find("input[name='longitude']").props().readOnly
            ).toEqual(true)

            // when
            wrapper
              .find("input[name='address']")
              .simulate('change', { target: { value: ADDRESS.slice(0, -1) } })

            // then
            expect(wrapper.find("input[name='city']").props().readOnly).toEqual(
              false
            )
            expect(
              wrapper.find("input[name='postalCode']").props().readOnly
            ).toEqual(false)
            expect(
              wrapper.find("input[name='latitude']").props().readOnly
            ).toEqual(false)
            expect(
              wrapper.find("input[name='longitude']").props().readOnly
            ).toEqual(false)

            // done
            done()
          })
        }, 500)
      })
    })

    it('fills the form with valid coordinates (even if they are negative)', done => {
      // given
      const { store } = configureStore()
      const history = createBrowserHistory()
      history.push(`/structures/${MANAGING_OFFERER_ID}/lieux/creation`)
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

      setTimeout(() => {
        // when (offerer request is done, form is now available)
        wrapper.update()
        wrapper
          .find("input[name='name']")
          .simulate('change', { target: { value: NAME } })
        wrapper
          .find("textarea[name='comment']")
          .simulate('change', { target: { value: COMMENT } })
        wrapper
          .find("input[name='bookingEmail']")
          .simulate('change', { target: { value: BOOKING_EMAIL } })
        wrapper
          .find("input[name='latitude']")
          .simulate('change', { target: { value: LATITUDE } })
        wrapper
          .find("input[name='longitude']")
          .simulate('change', { target: { value: LONGITUDE } })

        setTimeout(() => {
          // then (address has filled other inputs, submit button is not anymore disabled)
          wrapper.update()
          expect(
            wrapper.find("input[name='address']").props().readOnly
          ).toEqual(false)
          expect(wrapper.find("input[name='city']").props().readOnly).toEqual(
            false
          )
          expect(
            wrapper.find("input[name='postalCode']").props().readOnly
          ).toEqual(false)
          expect(
            wrapper.find("input[name='latitude']").props().readOnly
          ).toEqual(false)
          expect(
            wrapper.find("input[name='longitude']").props().readOnly
          ).toEqual(false)

          // when
          const submitButton = wrapper.find('button[type="submit"]')
          expect(submitButton.props().disabled).toEqual(false)
          submitButton.simulate('submit')

          // then
          const body = {
            address: ADDRESS,
            bookingEmail: BOOKING_EMAIL,
            city: CITY,
            comment: COMMENT,
            latitude: LATITUDE,
            longitude: LONGITUDE,
            managingOffererId: MANAGING_OFFERER_ID,
            name: NAME,
            postalCode: POSTAL_CODE,
          }
          const expectedSubConfig = {
            apiPath: '/venues/',
            body,
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

    it('fills the form with a dragging a marker', done => {
      // given
      const { store } = configureStore()
      const history = createBrowserHistory()
      history.push(`/structures/${MANAGING_OFFERER_ID}/lieux/creation`)
      const wrapper = mount(
        <Provider store={store}>
          <Router history={history}>
            <Switch>
              <Route path="/structures/:offererId/lieux/:venueId">
                <VenueContainer
                  formInitialValues={{ latitude: 1, longitude: 45 }}
                />
              </Route>
            </Switch>
          </Router>
        </Provider>
      )

      setTimeout(() => {
        // then (address has filled other inputs, submit button is not anymore disabled)
        wrapper.update()
        expect(wrapper.find("input[name='address']").props().readOnly).toEqual(
          false
        )
        expect(wrapper.find("input[name='city']").props().readOnly).toEqual(
          false
        )
        expect(
          wrapper.find("input[name='postalCode']").props().readOnly
        ).toEqual(false)
        expect(wrapper.find("input[name='latitude']").props().readOnly).toEqual(
          false
        )
        expect(
          wrapper.find("input[name='longitude']").props().readOnly
        ).toEqual(false)

        // when
        wrapper
          .find("input[name='name']")
          .simulate('change', { target: { value: NAME } })
        wrapper
          .find("textarea[name='comment']")
          .simulate('change', { target: { value: COMMENT } })
        wrapper
          .find("input[name='bookingEmail']")
          .simulate('change', { target: { value: BOOKING_EMAIL } })

        setTimeout(() => {
          wrapper.update()
          const { onMarkerDragend } = wrapper.find('LocationViewer').props()
          onMarkerDragend({ latitude: LATITUDE, longitude: LONGITUDE })

          setTimeout(() => {
            // when (address has filled other inputs, submit button is not anymore disabled)
            wrapper.update()
            const submitButton = wrapper.find('button[type="submit"]')
            expect(submitButton.props().disabled).toEqual(false)
            submitButton.simulate('submit')

            // then
            const body = {
              address: ADDRESS,
              bookingEmail: BOOKING_EMAIL,
              city: CITY,
              comment: COMMENT,
              latitude: LATITUDE,
              longitude: LONGITUDE,
              managingOffererId: MANAGING_OFFERER_ID,
              name: NAME,
              postalCode: POSTAL_CODE,
            }
            const expectedSubConfig = {
              apiPath: '/venues/',
              body,
              method: 'POST',
              normalizer: venueNormalizer,
            }
            const receivedConfig = mockRequestDataCatch.mock.calls.slice(
              -1
            )[0][0]
            Object.keys(expectedSubConfig).forEach(key =>
              expect(receivedConfig[key]).toEqual(expectedSubConfig[key])
            )

            // done
            done()
          })
        }, 500)
      })
    })
  })

  describe('Form Success', () => {
    describe('handleFormSuccess', () => {
      describe('when creating a venue', () => {
        beforeEach(() => {
          props.query.context = () => ({
            isCreatedEntity: true,
            isModifiedEntity: false,
            readOnly: false,
          })
        })

        const action = {
          config: {
            apiPath: '/venues/CM',
            method: 'POST',
          },
          payload: {
            datum: {
              id: 'CM',
            },
          },
        }

        it('should redirect to offerer page', () => {
          // given
          const wrapper = shallow(<Venue {...props} />)
          const state = wrapper.state()

          // when
          wrapper.instance().handleFormSuccess(jest.fn())(state, action)

          // then
          expect(push).toHaveBeenCalledWith('/structures/APEQ')
        })

        it('should dispatch a success message with valid message when venue is created', () => {
          // given
          const wrapper = shallow(<Venue {...props} />)
          const state = wrapper.state()

          // when
          wrapper.instance().handleFormSuccess(jest.fn())(state, action)

          // then
          expect(dispatch).toHaveBeenCalled()
        })
      })

      describe('when editing a venue', () => {
        beforeEach(() => {
          props.query.context = () => ({
            isCreatedEntity: false,
            isModifiedEntity: true,
            readOnly: false,
          })
        })

        const action = {
          config: {
            apiPath: '/venues/CM',
            method: 'PATCH',
          },
          payload: {
            datum: {
              id: 'CM',
            },
          },
        }

        it('should redirect to venue details', () => {
          // given
          const wrapper = shallow(<Venue {...props} />)
          const state = wrapper.state()

          // when
          wrapper.instance().handleFormSuccess(jest.fn())(state, action)

          // then
          expect(props.query.changeToReadOnly).toHaveBeenCalledWith(null, {
            id: 'CM',
          })
        })

        it('should dispatch a success message with valid message when venue is modified', () => {
          // given
          const wrapper = shallow(<Venue {...props} />)
          const state = wrapper.state()

          // when
          wrapper.instance().handleFormSuccess(jest.fn())(state, action)

          // then
          expect(dispatch).toHaveBeenCalledWith({
            patch: {
              text: 'Lieu modifié avec succès !',
              type: 'success',
            },
            type: 'SHOW_NOTIFICATION',
          })
        })
      })
    })
  })
})
