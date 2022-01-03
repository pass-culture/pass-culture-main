/*
 * @debt complexity "Gaël: the file contains eslint error(s) based on our new config"
 * @debt complexity "Gaël: file nested too deep in directory structure"
 * @debt rtl "Gaël: migration from enzyme to RTL"
 */

import { mount, shallow } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router-dom'

import * as usersSelectors from 'store/selectors/data/usersSelectors'
import { configureTestStore } from 'store/testUtils'

import AddressField from '../../fields/LocationFields/AddressField'
import LocationFields from '../../fields/LocationFields/LocationFields'
import VenueCreation from '../VenueCreation'

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
      venueTypes: [],
      venueLabels: [],
    }
  })

  describe('render', () => {
    it('should render component with default state', () => {
      // when
      const wrapper = shallow(<VenueCreation {...props} />)

      // then
      expect(wrapper.state('isRequestPending')).toBe(false)
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
        const wrapper = shallow(<VenueCreation {...props} />)

        // then
        expect(wrapper.state('isRequestPending')).toBe(false)
      })

      it('should display proper title', () => {
        // when
        const wrapper = shallow(<VenueCreation {...props} />)

        // then
        const title = wrapper.find({
          children: 'Ajoutez un lieu où accéder à vos offres.',
        })
        expect(title).toHaveLength(1)
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
        const wrapper = shallow(<VenueCreation {...props} />)

        // then
        expect(wrapper.state('isRequestPending')).toBe(false)
      })

      it('should be able to edit address field when venue has no SIRET', () => {
        // given
        props.formInitialValues = {
          siret: null,
        }

        jest
          .spyOn(usersSelectors, 'selectCurrentUser')
          .mockReturnValue({ currentUser: 'fakeUser', publicName: 'fakeName' })

        props.venue = {
          publicName: 'fake public name',
        }

        const store = configureTestStore()
        const history = createBrowserHistory()
        history.push(`/structures/AE/lieux/TR?modification`)

        let wrapper = mount(
          <Provider store={store}>
            <Router history={history}>
              <VenueCreation {...props} />
            </Router>
          </Provider>
        )

        let addressField = wrapper
          .find(LocationFields)
          .find(AddressField)
          .find('input.field-address')
          .first()

        addressField.simulate('change', {
          target: { value: 'Addresse de test' },
        })

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
        const wrapper = shallow(<VenueCreation {...props} />)

        // then
        expect(wrapper.state('isRequestPending')).toBe(false)
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

        it('should redirect to homepage with selected offerer', () => {
          // given
          const wrapper = shallow(<VenueCreation {...props} />)
          const state = wrapper.state()

          // when
          wrapper.instance().handleFormSuccess(jest.fn())(state, action)

          // then
          expect(push).toHaveBeenCalledWith('/accueil?structure=APEQ')
        })

        it('should call handleSubmitRequestSuccess with the right parameters when venue is created', () => {
          // given
          const wrapper = shallow(<VenueCreation {...props} />)
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
      })
    })
  })
})
