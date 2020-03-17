import { mount, shallow } from 'enzyme'
import { createBrowserHistory, createMemoryHistory } from 'history'
import React from 'react'
import { Form } from 'react-final-form'
import { Provider } from 'react-redux'
import { Router } from 'react-router-dom'
import * as reactReduxLogin from 'with-react-redux-login'
import configureStore from '../../../../utils/store'
import AddressField from '../fields/LocationFields/AddressField'
import LocationFields from '../fields/LocationFields/LocationFields'

import Venue from '../Venue'
import VenueProvidersManagerContainer from '../VenueProvidersManager/VenueProvidersManagerContainer'

describe('src | components | pages | Venue', () => {
  let push
  let props

  beforeEach(() => {
    push = jest.fn()
    props = {
      formInitialValues: {
        id: 'CM',
      },
      history: {
        location: {
          pathname: '/fake',
        },
        push: push,
      },
      handleInitialRequest: jest.fn(),
      handleSubmitRequest: jest.fn(),
      handleSubmitRequestSuccess: jest.fn(),
      handleSubmitRequestFail: jest.fn(),
      match: {
        params: {
          offererId: 'APEQ',
          venueId: 'AQYQ',
        },
      },
      offerer: {
        id: 'BQ',
        name: 'Maison du chocolat',
      },
      query: {
        changeToReadOnly: jest.fn(),
        context: jest.fn().mockReturnValue({
          isCreatedEntity: true,
          isModifiedEntity: false,
          readOnly: false,
        }),
      },
      trackCreateVenue: jest.fn(),
      trackModifyVenue: jest.fn(),
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<Venue {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
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

      it('should display proper title', () => {
        // when
        const wrapper = shallow(<Venue {...props} />)

        // then
        const title = wrapper.find({ children: 'Ajoutez un lieu où accéder à vos offres.' })
        expect(title).toHaveLength(1)
      })

      it('should build the proper backTo link', () => {
        // when
        const wrapper = shallow(<Venue {...props} />)

        // then
        expect(wrapper.prop('backTo')).toStrictEqual({
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

      it('should be able to edit address field when venue has no SIRET', () => {
        // given
        props.formInitialValues = {
          siret: null,
        }

        jest
          .spyOn(reactReduxLogin, 'selectCurrentUser')
          .mockReturnValue({ currentUser: 'fakeUser' })

        props.venue = {
          publicName: 'fake public name',
        }

        const { store } = configureStore()
        const history = createBrowserHistory()
        history.push(`/structures/AE/lieux/TR?modification`)

        let wrapper = mount(
          <Provider store={store}>
            <Router history={history}>
              <Venue {...props} />
            </Router>
          </Provider>
        )

        let addressField = wrapper
          .find(LocationFields)
          .find(AddressField)
          .find('input.field-address')
          .first()

        addressField.simulate('change', { target: { value: 'Addresse de test' } })

        wrapper = wrapper.update()

        addressField = wrapper
          .find(LocationFields)
          .find(AddressField)
          .find('input.field-address')
          .first()

        // then
        expect(addressField.prop('value')).toBe('Addresse de test')
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

      describe('create new offer link', () => {
        it('should redirect to offer creation page', () => {
          // given
          jest
            .spyOn(reactReduxLogin, 'selectCurrentUser')
            .mockReturnValue({ currentUser: 'fakeUser' })

          props.venue = {
            publicName: 'fake public name',
          }

          const { store } = configureStore()
          const history = createMemoryHistory()
          history.push('/structures/APEQ/lieux/CM')

          let wrapper = mount(
            <Provider store={store}>
              <Router history={history}>
                <Venue
                  {...props}
                  history={history}
                />
              </Router>
            </Provider>
          )
          const createOfferLink = wrapper.find({ children: 'Créer une offre' })

          // when
          createOfferLink.simulate('click', { button: 0 })

          // then
          expect(`${history.location.pathname}${history.location.search}`).toBe(
            '/offres/creation?lieu=CM&structure=APEQ'
          )
        })
      })
    })
  })

  describe('form Success', () => {
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

        it('should call handleSubmitRequestSuccess with the right parameters when venue is created', () => {
          // given
          const wrapper = shallow(<Venue {...props} />)
          const state = wrapper.state()

          // when
          wrapper.instance().handleFormSuccess(jest.fn())(state, action)

          // then
          expect(props.handleSubmitRequestSuccess).toHaveBeenCalledWith(
            { isRequestPending: false },
            {
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
          )
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

          it('should change query to read only null', () => {
            // given
            const wrapper = shallow(<Venue {...props} />)
            const state = wrapper.state()

            // when
            wrapper.instance().handleFormSuccess(jest.fn())(state, action)

            // then
            expect(props.query.changeToReadOnly).toHaveBeenCalledWith(null)
          })

          it('should call handleSubmitRequestSuccess with the right parameters when venue is modified', () => {
            // given
            const wrapper = shallow(<Venue {...props} />)
            const state = wrapper.state()

            // when
            wrapper.instance().handleFormSuccess(jest.fn())(state, action)

            // then
            expect(props.handleSubmitRequestSuccess).toHaveBeenCalledWith(
              { isRequestPending: false },
              {
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
            )
          })
        })
      })
    })
  })

  describe('event tracking', () => {
    it('should track venue creation', () => {
      // given
      const state = {}
      const action = {
        payload: {
          datum: {
            id: 'Ty5645dgfd',
          },
        },
      }
      const wrapper = shallow(<Venue {...props} />)
      const formResolver = jest.fn()

      // when
      wrapper.instance().handleFormSuccess(formResolver)(state, action)

      // then
      expect(props.trackCreateVenue).toHaveBeenCalledWith('Ty5645dgfd')
    })

    it('should track venue update', () => {
      // given
      const state = {}

      jest.spyOn(props.query, 'context').mockReturnValue({
        isCreatedEntity: false,
        isModifiedEntity: false,
        readOnly: false,
      })

      const action = {
        payload: {
          datum: {
            id: 'Ty5645dgfd',
          },
        },
      }
      const wrapper = shallow(<Venue {...props} />)
      const formResolver = jest.fn()

      // when
      wrapper.instance().handleFormSuccess(formResolver)(state, action)

      // then
      expect(props.trackModifyVenue).toHaveBeenCalledWith('CM')
    })
  })
})
