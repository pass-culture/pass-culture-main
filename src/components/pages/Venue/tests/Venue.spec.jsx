import React from 'react'
import Venue from '../Venue'
import { shallow } from 'enzyme'
import HeroSection from 'components/layout/HeroSection'
import { CancelButton, Field, Form, SubmitButton } from 'pass-culture-shared'
import { NavLink } from 'react-router-dom'
import VenueProvidersManager from '../VenueProvidersManager'

describe('src | components | pages | Venue | Venue', () => {
  const dispatch = jest.fn()
  let props

  beforeEach(() => {
    props = {
      currentUser: {},
      dispatch: dispatch,
      formComment: null,
      formLatitude: 5.15981,
      formLongitude: -52.63452,
      formSiret: '22222222411111',
      history: {},
      location: {
        search: '',
      },
      match: {
        params: {
          offererId: 'APEQ',
          venueId: 'AQYQ',
        },
      },
      name: 'Maison de la Brique',
      offerer: {},
      user: {},
      venuePatch: {
        id: null,
      },
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
      expect(wrapper.state('isLoading')).toBe(false)
      expect(wrapper.state('isNew')).toBe(false)
      expect(wrapper.state('isRead')).toBe(true)
    })

    it('should not render a Form when venue is virtual', () => {
      // given
      props.venuePatch = {
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
          label: 'STRUCTURE',
          path: '/structures/APEQ',
        })
      })

      it('should display a hidden Field component', () => {
        // when
        const wrapper = shallow(<Venue {...props} />)

        // then
        const field = wrapper
          .find(Form)
          .find(Field)
          .first()
        expect(field).toBeDefined()
        expect(field.prop('type')).toBe('hidden')
        expect(field.prop('name')).toBe('managingOffererId')
      })

      it('should display a CancelButton component', () => {
        // when
        const wrapper = shallow(<Venue {...props} />)

        // then
        const cancelButton = wrapper.find(CancelButton)
        expect(cancelButton).toBeDefined()
        expect(cancelButton.prop('to')).toBe('/structures/APEQ')
      })

      it('should display a SubmitButton component', () => {
        // when
        const wrapper = shallow(<Venue {...props} />)

        // then
        const submitButton = wrapper.find(SubmitButton)
        expect(submitButton.dive().text()).toBe('Créer')
      })

      it('should display a comment Field component', () => {
        // when
        const wrapper = shallow(<Venue {...props} />)

        // then
        const firstFieldGroup = wrapper.find('.field-group').first()
        const lastField = firstFieldGroup.find(Field).last()
        expect(lastField).toBeDefined()
        expect(lastField.prop('label')).toBe('Commentaire (si pas de SIRET)')
        expect(lastField.prop('name')).toBe('comment')
        expect(lastField.prop('type')).toBe('textarea')
        expect(lastField.prop('required')).toBe(false)
      })

      it('should not display a NavLink component', () => {
        // when
        const wrapper = shallow(<Venue {...props} />)

        // then
        const heroSection = wrapper.find(HeroSection)
        expect(heroSection.find(NavLink)).toHaveLength(0)
      })

      it('should not display a VenueProvidersManager component', () => {
        // when
        const wrapper = shallow(<Venue {...props} />)

        // then
        expect(wrapper.find(VenueProvidersManager)).toHaveLength(0)
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
      })

      it('should permit user to change the e-mail', () => {
        // when
        const wrapper = shallow(<Venue {...props} />)
        const expected = {
          isEdit: true,
          isLoading: false,
          isNew: false,
          isRead: false,
        }

        // then
        expect(wrapper.state().isRead).toEqual(expected.isRead)
      })
    })
  })

  describe('functions', () => {
    describe('when patching a Venue', () => {
      const pushMock = jest.fn()
      const props = {
        currentUser: {},
        dispatch: dispatch,
        formComment: null,
        formLatitude: 5.15981,
        formLongitude: -52.63452,
        formSiret: '22222222411111',
        history: {
          location: {
            pathname: '/fake',
          },
          push: pushMock,
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
        name: 'Maison de la Brique',
        offerer: {
          id: 'BQ',
        },
        user: {},
        venuePatch: {},
      }
      const action = {
        config: {
          apiPath: '/venues/CM',
          method: 'PATCH',
        },
        payload: {
          datum: {
            bookingEmail: 'fake@email.com',
            id: 'CM',
          },
        },
        type: 'SUCCESS_DATA_PATCH_VENUES/CM',
      }

      it('should change pathname', () => {
        // // When
        const wrapper = shallow(<Venue {...props} />)
        wrapper.instance().handleSuccess(wrapper.state(), action)

        // Then
        expect(pushMock).toHaveBeenCalledWith('/structures/BQ/lieux/CM')
      })

      it('should dispatch a success message', () => {
        // When
        const wrapper = shallow(<Venue {...props} />)
        wrapper.instance().handleSuccess(wrapper.state(), action)

        const expected = {
          patch: {
            text: 'Lieu modifié avec succès !',
            type: 'success',
          },
          type: 'SHOW_NOTIFICATION',
        }

        // then
        expect(dispatch).toHaveBeenCalledWith(expected)
      })
    })
  })
})
