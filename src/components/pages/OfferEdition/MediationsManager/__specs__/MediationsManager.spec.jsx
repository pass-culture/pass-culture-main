import React from 'react'
import { shallow } from 'enzyme'

import MediationsManager, { NO_MEDIATION_TOOLTIP } from '../MediationsManager'
import { NavLink } from 'react-router-dom'
import { Icon } from 'pass-culture-shared'

describe('components | OfferEdition | MediationsManager', () => {
  let showNotification
  let closeNotification
  let props

  beforeEach(() => {
    showNotification = jest.fn()
    closeNotification = jest.fn()
    props = {
      showNotification,
      closeNotification,
      hasMediations: false,
      atLeastOneActiveMediation: false,
      mediations: [],
      notification: null,
      offer: {},
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<MediationsManager {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render()', () => {
    it('should display a notification when no mediation in offer', () => {
      // given
      props.notification = null
      props.hasMediations = false
      props.atLeastOneActiveMediation = false

      // when
      shallow(<MediationsManager {...props} />)

      // then
      expect(props.showNotification).toHaveBeenCalledWith({
        tag: 'mediations-manager',
        text:
          'Cette offre ne sera pas mise en avant dans l’application pass Culture mais sera accessible via la recherche par mots-clés.',
        tooltip: {
          children: (
            <span>
              {'Pourquoi ?'}
            </span>
          ),
          place: 'bottom',
          tip: NO_MEDIATION_TOOLTIP,
          type: 'info',
        },
        type: 'warning',
      })
    })

    it('should display a notification when no active mediation in offer', () => {
      // given
      props.notification = null
      props.hasMediations = true
      props.atLeastOneActiveMediation = false

      // when
      shallow(<MediationsManager {...props} />)

      // then
      expect(props.showNotification).toHaveBeenCalledWith({
        tag: 'mediations-manager',
        text:
          'Cette offre ne sera pas mise en avant dans l’application pass Culture mais sera accessible via la recherche par mots-clés.',
        tooltip: {
          children: (
            <span>
              {'Pourquoi ?'}
            </span>
          ),
          place: 'bottom',
          tip: NO_MEDIATION_TOOLTIP,
          type: 'info',
        },
        type: 'warning',
      })
    })

    it("shouldn't display a notification if a notification is already present", () => {
      // given
      props.hasMediations = true
      props.atLeastOneActiveMediation = false
      props.notification = { text: 'bla bla bla' }

      // when
      shallow(<MediationsManager {...props} />)

      // then
      expect(props.showNotification).not.toHaveBeenCalled()
    })

    it('should close notification when unmounting component', () => {
      // given
      props.notification = {
        tag: 'mediations-manager',
      }
      const wrapper = shallow(<MediationsManager {...props} />)

      // when
      wrapper.unmount()

      // then
      expect(props.closeNotification).toHaveBeenCalledWith()
    })

    it('should render a NavLink component when there is an offer', () => {
      // given
      props.offer = {
        id: 'ABC',
      }
      props.mediations = [ { id: 'A' }, { id: 'B' } ]

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
        id: 'ABC',
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
        id: 'ABC',
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
        id: 'ABC',
      }
      props.mediations = [ { id: 'A' }, { id: 'B' } ]

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
