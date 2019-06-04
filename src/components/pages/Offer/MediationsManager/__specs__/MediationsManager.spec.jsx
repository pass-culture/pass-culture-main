import React from 'react'
import { shallow } from 'enzyme'

import MediationsManager from '../MediationsManager'
import { NavLink } from 'react-router-dom'
import { Icon } from 'pass-culture-shared'

describe('src | components | pages | Offer | MediationsManager | MediationsManager', () => {
  let dispatch
  let props

  beforeEach(() => {
    dispatch = jest.fn()
    props = {
      dispatch,
      mediations: [],
      notification: null,
      offer: null
    }
  })

  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        dispatch: dispatch,
        mediations: [],
      }

      // when
      const wrapper = shallow(<MediationsManager {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('render', () => {
    it('should display a notification when no mediation', () => {
      // when
      shallow(<MediationsManager {...props} />)

      // then
      expect(dispatch).toHaveBeenCalledWith({
        patch: {
          tag: 'mediations-manager',
          text: 'Cette offre n\'apparaîtra pas dans l\'app pass Culture.',
          tooltip: {
            children: <a> Pourquoi ? </a>,
            place: 'bottom',
            tip: '<div><p>Pour que votre offre s\'affiche dans l\'application du Pass Culture, vous devez:</p><p>- ajouter une ou plusieurs accroches.</p></div>',
            type: 'info'
          },
          type: 'warning'
        },
        type: 'SHOW_NOTIFICATION'
      })
    })

    it('should close notification when unmounting component', () => {
      // given
      props.notification = {
        tag: 'mediations-manager'
      }
      const wrapper = shallow(<MediationsManager {...props} />)

      // when
      wrapper.unmount()

      // then
      expect(dispatch.mock.calls[1][0]).toEqual({type: 'CLOSE_NOTIFICATION'})
    })

    it('should render a NavLink component when there is an offer', () => {
      // given
      props.offer = {
        id: 'ABC'
      }
      props.mediations = [{id: 'A'}, {id: 'B'}]

      // when
      const wrapper = shallow(<MediationsManager {...props} />)

      // then
      const navLink = wrapper.find(NavLink)
      expect(navLink).toHaveLength(1)
      expect(navLink.prop('className')).toBe('button is-primary is-outlined')
      expect(navLink.prop('to')).toBe('/offres/ABC/accroches/nouveau')
    })

    it('should render 2 spans element containing the right info', () => {
      // given
      props.offer = {
        id: 'ABC'
      }
      props.mediations = []

      // when
      const wrapper = shallow(<MediationsManager {...props} />)

      // then
      const spans = wrapper.find('span')
      expect(spans).toHaveLength(2)
      expect(spans.at(0).find(Icon)).toHaveLength(1)
      expect(spans.at(1).text()).toBe('Ajouter une accroche')
    })

    it('should render an Icon component with the prop ico-stars-w when no mediation', () => {
      // given
      props.offer = {
        id: 'ABC'
      }
      props.mediations = []

      // when
      const wrapper = shallow(<MediationsManager {...props} />)

      // then
      const navLink = wrapper.find(NavLink)
      const spans = navLink.find('span')
      const icon = spans.at(0).find(Icon)
      expect(icon).toHaveLength(1)
      expect(icon.prop('svg')).toBe('ico-stars-w')
    })

    it('should render an Icon component with the prop ico-stars when mediations', () => {
      // given
      props.offer = {
        id: 'ABC'
      }
      props.mediations = [{id: 'A'}, {id: 'B'}]

      // when
      const wrapper = shallow(<MediationsManager {...props} />)

      // then
      const navLink = wrapper.find(NavLink)
      const spans = navLink.find('span')
      const icon = spans.at(0).find(Icon)
      expect(icon).toHaveLength(1)
      expect(icon.prop('svg')).toBe('ico-stars')
    })
  })
})
