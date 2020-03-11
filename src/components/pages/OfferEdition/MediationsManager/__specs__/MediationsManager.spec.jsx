import React from 'react'
import { shallow } from 'enzyme'

import MediationsManager from '../MediationsManager'
import { NavLink } from 'react-router-dom'
import { Icon } from 'pass-culture-shared'

describe('src | components | pages | OfferEdition | MediationsManager | MediationsManager', () => {
  let props

  beforeEach(() => {
    props = {
      hasMediations: false,
      atLeastOneActiveMediation: false,
      mediations: [],
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
    describe('when no mediation in offer', () => {
      it('should display an information message', () => {
        // given
        props.hasMediations = false
        props.atLeastOneActiveMediation = false

        // when
        const wrapper = shallow(<MediationsManager {...props} />)
        const informationMessageWrapper = wrapper.findWhere(htmlElement =>
          htmlElement
            .text()
            .includes("Ajoutez une accroche pour mettre cette offre en avant dans l'application")
        )

        // then
        expect(informationMessageWrapper.exists()).toBe(true)
      })

      it('should a NavLink with a icon and info message inside', () => {
        // given
        props.offer = {
          id: 'ABC',
        }
        props.mediations = []

        // when
        const wrapper = shallow(<MediationsManager {...props} />)

        // then
        const lienAjoutAccroche = wrapper.find(NavLink)
        expect(lienAjoutAccroche.exists()).toBe(true)
        const spans = wrapper.find('span')
        expect(spans).toHaveLength(2)
        expect(spans.at(0).find(Icon)).toHaveLength(1)
        expect(spans.at(1).text()).toBe('Ajouter une accroche')
      })

      it('should render a NavLink with an Icon inside', () => {
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
    })

    describe('when no active mediation in offer', () => {
      it('should display an information message', () => {
        // given
        props.hasMediations = true
        props.atLeastOneActiveMediation = false

        // when
        const wrapper = shallow(<MediationsManager {...props} />)
        const informationMessageWrapper = wrapper.findWhere(htmlElement =>
          htmlElement
            .text()
            .includes("Ajoutez une accroche pour mettre cette offre en avant dans l'application")
        )

        // then
        expect(informationMessageWrapper.exists()).toBe(true)
      })
    })

    describe('when there is an offer and an active mediation', () => {
      it('should render a NavLink component', () => {
        // given
        props.offer = {
          id: 'ABC',
        }
        props.mediations = [{ id: 'A', isActive: true }, { id: 'B', isActive: true }]

        // when
        const wrapper = shallow(<MediationsManager {...props} />)

        // then
        const navLink = wrapper.find(NavLink)
        expect(navLink).toHaveLength(1)
        expect(navLink.prop('className')).toBe('button is-primary is-outlined')
        expect(navLink.prop('to')).toBe('/offres/ABC/accroches/nouveau')
      })

      it('should render an Icon component with the prop ico-stars when mediations', () => {
        // given
        props.offer = {
          id: 'ABC',
        }
        props.mediations = [{ id: 'A' }, { id: 'B' }]

        // when
        const wrapper = shallow(<MediationsManager {...props} />)

        // then
        const navLink = wrapper.find(NavLink)
        const spans = navLink.find('span')
        const icon = spans.at(0).find(Icon)
        expect(icon).toHaveLength(1)
        expect(icon.prop('svg')).toBe('ico-stars')
      })

      it('should not display an information message', () => {
        // given
        props.hasMediations = true
        props.atLeastOneActiveMediation = true

        // when
        const wrapper = shallow(<MediationsManager {...props} />)
        const informationMessageWrapper = wrapper.findWhere(htmlElement =>
          htmlElement
            .text()
            .includes("Ajoutez une accroche pour mettre cette offre en avant dans l'application")
        )

        // then
        expect(informationMessageWrapper.exists()).toBe(false)
      })
    })
  })
})
