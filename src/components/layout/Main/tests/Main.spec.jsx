import { shallow } from 'enzyme'
import { Modal } from 'pass-culture-shared'
import React from 'react'
import { NavLink } from 'react-router-dom'
import ReactTooltip from 'react-tooltip'

import HeaderContainer from '../../Header/HeaderContainer'
import NotificationV1Container from '../../NotificationV1/NotificationV1Container'
import NotificationV2Container from '../../NotificationV2/NotificationV2Container'
import Main from '../Main'

describe('src | components | layout | Main', () => {
  describe('render', () => {
    let props
    beforeEach(() => {
      props = {
        children: [{}],
        currentUser: {},
        dispatch: jest.fn(),
        fullscreen: true,
        location: {},
        name: 'nom',
        Tag: 'main',
        backTo: {
          path: 'other page',
          label: 'other page label',
        },
      }
    })

    it('should always render ReactTooltip and Modal components', () => {
      // When
      const wrapper = shallow(<Main {...props} />)

      // Then
      expect(wrapper.find(ReactTooltip)).toHaveLength(1)
      expect(wrapper.find(Modal)).toHaveLength(1)
    })

    describe('when in fullscreen mode', () => {
      it('should not render a header container', () => {
        // Given
        props.fullscreen = true

        // When
        const wrapper = shallow(<Main {...props} />)

        // Then
        expect(wrapper.find(HeaderContainer)).toHaveLength(0)
      })

      it('should render a notification container with isFullscreen props', () => {
        // Given
        props.fullscreen = true

        // When
        const wrapper = shallow(<Main {...props} />)

        // Then
        expect(wrapper.find(NotificationV1Container).prop('isFullscreen')).toBe(true)
      })

      it('should render the new notification container', () => {
        // Given
        props.fullscreen = true

        // When
        const wrapper = shallow(<Main {...props} />)

        // Then
        expect(wrapper.find(NotificationV2Container)).toHaveLength(1)
      })
    })

    describe('when not in fullscreen mode', () => {
      it('should render a header container', () => {
        // Given
        props.fullscreen = false

        // When
        const wrapper = shallow(<Main {...props} />)

        // Then
        expect(wrapper.find(HeaderContainer)).toHaveLength(1)
      })

      it('should render a navlink component if backTo is defined', () => {
        // Given
        props.fullscreen = false
        props.backTo = { path: '' }

        // When
        const wrapper = shallow(<Main {...props} />)

        // Then
        expect(wrapper.find(NavLink)).toHaveLength(1)
      })

      it('should render the new notification container', () => {
        // Given
        props.fullscreen = false

        // When
        const wrapper = shallow(<Main {...props} />)

        // Then
        expect(wrapper.find(NotificationV2Container)).toHaveLength(1)
      })
    })
  })
})
