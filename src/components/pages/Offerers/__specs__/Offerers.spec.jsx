import React from 'react'
import { shallow } from 'enzyme'

import Offerers from '../Offerers'

describe('src | components | pages | Offerers | Offerers', () => {
  let props

  beforeEach(() => {
    props = {
      assignData:jest.fn(),
      closeNotification:jest.fn(),
      currentUser: {},
      dispatch:jest.fn(),
      loadOfferers:jest.fn(),
      loadNotValidatedUserOfferers:jest.fn(),
      offerers: [{ id: 'AE' }],
      pendingOfferers: [],
      pagination: {
        apiQuery: {
          keywords: null,
        },
      },
      query: {
        change: jest.fn(),
        parse: () => ({ 'mots-cles': null }),
      },
      showNotification:jest.fn(),
      location: {
        search: '',
      },
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<Offerers {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    describe('should pluralize offerers menu link', () => {
      it('should display Votre structure when one offerer', () => {
        // given
        props.currentUser = {}
        props.offerers = [{ id: 'AE' }]
        props.pendingOfferers = []

        // when
        const wrapper = shallow(<Offerers {...props} />)
        const heroSection = wrapper.find('HeroSection').props()

        // then
        expect(heroSection.title).toStrictEqual('Votre structure juridique')
      })

      it('should display Vos structures when many offerers', () => {
        // given
        props.currentUser = {}
        props.offerers = [{ id: 'AE' }, { id: 'AF' }]
        props.pendingOfferers = []

        // when
        const wrapper = shallow(<Offerers {...props} />)
        const heroSection = wrapper.find('HeroSection').props()

        // then
        expect(heroSection.title).toStrictEqual('Vos structures juridiques')
      })
    })

    describe('when leaving page', () => {
      it('should not close notifcation', () => {
        // given
        props = {...props, closeNotification: jest.fn()}
        const wrapper = shallow(<Offerers {...props} />)

        // when
        wrapper.unmount()

        // then
        expect(props.closeNotification).not.toHaveBeenCalled()
      })

      it('should close offerer notifcation', () => {
        // given
        props = {
          ...props,
          closeNotification: jest.fn(),
          notification: {
            tag: 'offerers'
          }
        }
        const wrapper = shallow(<Offerers {...props} />)

        // when
        wrapper.unmount()

        // then
        expect(props.closeNotification).toHaveBeenCalledWith()
      })

      it('should not fail on null notifcation', () => {
        // given
        props = {
          ...props,
          closeNotification: jest.fn(),
          notification: null
        }
        const wrapper = shallow(<Offerers {...props} />)

        // when
        wrapper.unmount()

        // then
        expect(props.closeNotification).not.toHaveBeenCalledWith()
      })
    })
  })
})
