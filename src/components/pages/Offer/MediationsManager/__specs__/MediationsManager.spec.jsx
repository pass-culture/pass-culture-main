import { shallow } from 'enzyme'
import React from 'react'
import { Link } from 'react-router-dom'

import MediationsManager from '../MediationsManager'
import { SVGStars } from 'components/svg/SVGStars'

describe('src | MediationsManager', () => {
  let props

  beforeEach(() => {
    props = {
      hasMediations: false,
      atLeastOneActiveMediation: false,
      mediations: [],
      offer: {},
    }
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
            .includes("Ajoutez une accroche pour mettre cette offre en avant dans l'application.")
        )

        // then
        expect(informationMessageWrapper.exists()).toBe(true)
      })

      it('should render a Link with a icon and info message inside', () => {
        // given
        props.offer = {
          id: 'ABC',
        }
        props.mediations = []

        // when
        const wrapper = shallow(<MediationsManager {...props} />)

        // then
        const addMediationLink = wrapper.find(Link)
        expect(addMediationLink.exists()).toBe(true)
        expect(addMediationLink.find(SVGStars)).toHaveLength(1)
        expect(wrapper.find('span').text()).toBe('Ajouter une accroche')
      })

      it('should render a Link with an Icon inside', () => {
        // given
        props.offer = {
          id: 'ABC',
        }
        props.mediations = []

        // when
        const wrapper = shallow(<MediationsManager {...props} />)

        // then
        const navLink = wrapper.find(Link)
        expect(navLink.find(SVGStars)).toHaveLength(1)
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
      it('should render a Link component', () => {
        // given
        props.offer = {
          id: 'ABC',
        }
        props.mediations = [{ id: 'A', isActive: true }, { id: 'B', isActive: true }]

        // when
        const wrapper = shallow(<MediationsManager {...props} />)

        // then
        const navLink = wrapper.find(Link)
        expect(navLink).toHaveLength(1)
        expect(navLink.prop('to')).toBe('/offres/ABC/accroches/nouveau')
      })

      it('should render an Icon component with the correct icon when mediations', () => {
        // given
        props.offer = {
          id: 'ABC',
        }
        props.mediations = [{ id: 'A', isActive: true }, { id: 'B', isActive: true }]

        // when
        const wrapper = shallow(<MediationsManager {...props} />)

        // then
        const navLink = wrapper.find(Link)
        expect(navLink.find(SVGStars)).toHaveLength(1)
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
