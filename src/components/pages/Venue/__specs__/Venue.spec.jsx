import { shallow } from 'enzyme'
import React from 'react'
import { Form } from 'react-final-form'

import Venue from '../Venue'
import { mapDispatchToProps } from '../VenueContainer'
import VenueProvidersManagerContainer from '../VenueProvidersManager/VenueProvidersManagerContainer'
import HeroSection from 'components/layout/HeroSection'

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
