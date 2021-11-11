import { shallow } from 'enzyme'
import React from 'react'

import BookingSuccess from '../BookingSuccess'

describe('src | components | BookingSuccess', () => {
  const NO_BREAK_SPACE = '\u00A0'
  let props

  beforeEach(() => {
    props = {
      price: 12.5,
      token: 'G8G8G8',
    }
  })

  describe('when booking an event', () => {
    it('should display texts', () => {
      // given
      props.isEvent = true
      props.offerUrl = null
      props.quantity = 1

      // when
      const wrapper = shallow(<BookingSuccess {...props} />)

      // then
      const title = wrapper.find('h3')
      const sentence1 = wrapper.find('p').at(0)
      const sentence3 = wrapper.find('p').at(2)
      expect(title.text()).toBe('<Icon />Ta réservation est validée.')
      expect(sentence1.text()).toBe(
        `12,5${NO_BREAK_SPACE}€ ont été déduits de ton pass.Présente le code suivant sur place :`
      )
      expect(sentence3.text()).toBe(
        'Retrouve ce code et les détails de l’offre dansla rubrique Réservations de ton compte'
      )
    })

    it('should display an other title when its a duo offer', () => {
      // given
      props.isEvent = true
      props.quantity = 2

      // when
      const wrapper = shallow(<BookingSuccess {...props} />)

      // then
      const title = wrapper.find('h3')
      expect(title.text()).toBe('<Icon />Ta réservation duo est validée.')
    })
  })

  describe('when booking a thing', () => {
    it('should display an other sentence', () => {
      // given
      props.isEvent = false
      props.offerUrl = 'http://fake-url.com'
      props.quantity = 1

      // when
      const wrapper = shallow(<BookingSuccess {...props} />)

      // then
      const title = wrapper.find('h3')
      const sentence1 = wrapper.find('p').at(0)
      const sentence2 = wrapper.find('p a')
      const sentence3 = wrapper.find('p').at(2)
      expect(title.text()).toBe('<Icon />Tu peux accéder à cette offre à tout moment.')
      expect(sentence1.text()).toBe(`12,5${NO_BREAK_SPACE}€ ont été déduits de ton pass.`)
      expect(sentence2.text()).toBe('Accéder à l’offre numérique')
      expect(sentence2.prop('href')).toBe('http://fake-url.com')
      expect(sentence2.prop('rel')).toBe('noopener noreferrer')
      expect(sentence2.prop('target')).toBe('_blank')
      expect(sentence3.text()).toBe(
        'Retrouve l’adresse Internet et les détails del’offre dans la rubrique Réservations de ton compte'
      )
    })

    describe('when the offer as some activation codes', () => {
      it('is displayed with expiration date', () => {
        // given
        props.isEvent = false
        props.offerUrl = 'http://fake-url.com'
        props.quantity = 1
        props.activationCode = {
          code: 'code-bQetgWSSK',
          expirationDate: '2020-12-23T09:00:00.000000Z',
        }

        // when
        const wrapper = shallow(<BookingSuccess {...props} />)

        // then
        const title = wrapper.find('h3')
        const sentence1 = wrapper.find('p').at(0)
        const sentence2 = wrapper.find('p a')
        const sentence3 = wrapper.find('p').at(2)
        expect(title.text()).toBe(
          "<Icon />Ton code d’activation : code-bQetgWSSK A activer avant le 23 décembre 2020."
        )
        expect(sentence1.text()).toBe(`12,5${NO_BREAK_SPACE}€ ont été déduits de ton pass.`)
        expect(sentence2.text()).toBe('Accéder à l’offre numérique')
        expect(sentence2.prop('href')).toBe('http://fake-url.com')
        expect(sentence2.prop('rel')).toBe('noopener noreferrer')
        expect(sentence2.prop('target')).toBe('_blank')
        expect(sentence3.text()).toBe(
          'Retrouve l’adresse Internet et les détails del’offre dans la rubrique Réservations de ton compte'
        )
      })

      it('is displayed without an expiration date', () => {
        // given
        props.isEvent = false
        props.offerUrl = 'http://fake-url.com'
        props.quantity = 1
        props.activationCode = {
          code: 'code-bQetgWSSK',
          expirationDate: null,
        }

        // when
        const wrapper = shallow(<BookingSuccess {...props} />)

        // then
        const title = wrapper.find('h3')
        const sentence1 = wrapper.find('p').at(0)
        const sentence2 = wrapper.find('p a')
        const sentence3 = wrapper.find('p').at(2)
        expect(title.text()).toBe("<Icon />Ton code d’activation : code-bQetgWSSK")
        expect(sentence1.text()).toBe(`12,5${NO_BREAK_SPACE}€ ont été déduits de ton pass.`)
        expect(sentence2.text()).toBe('Accéder à l’offre numérique')
        expect(sentence2.prop('href')).toBe('http://fake-url.com')
        expect(sentence2.prop('rel')).toBe('noopener noreferrer')
        expect(sentence2.prop('target')).toBe('_blank')
        expect(sentence3.text()).toBe(
          'Retrouve l’adresse Internet et les détails del’offre dans la rubrique Réservations de ton compte'
        )
      })
    })
  })
})
