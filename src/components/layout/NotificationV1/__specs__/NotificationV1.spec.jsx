import { shallow } from 'enzyme'
import React from 'react'

import Icon from 'components/layout/Icon'
import NotificationV1 from '../NotificationV1'

describe('src | components | layout | NotificationV1', () => {
  let props
  let dispatch

  beforeEach(() => {
    dispatch = jest.fn()
    props = {
      dispatch,
      notification: null,
    }
  })

  describe('render', () => {
    describe('warning notification with url and urlLabel', () => {
      it('should display correct info type with specific text and a link', () => {
        // given
        props.notification = {
          tag: 'offerers',
          text: 'Formulaire non validé',
          type: 'warning',
        }

        // when
        const wrapper = shallow(<NotificationV1 {...props} />)
        const link = wrapper.find('a')
        const icon = wrapper.find(Icon)
        const firstDiv = wrapper.find('div').at(0)
        const button = wrapper.find('button')

        // then
        expect(icon).toHaveLength(1)
        expect(link).toHaveLength(0)
        expect(firstDiv.prop('className')).toBe('notification is-warning')
        expect(icon.prop('png')).toBe('picto-warning-solid-orange-S')
        expect(button.text()).toStrictEqual('OK')
      })
    })

    describe('info notification with url and urlLabel', () => {
      it('should display correct info type with specific text and a link', () => {
        // given
        props.notification = {
          tag: 'offerers',
          text:
            'Commencez par créer un lieu pour accueillir vos offres physiques (événements, livres, abonnements…)',
          type: 'info',
          url: '/structures/AFPQ/lieux/creation',
          urlLabel: 'Nouveau lieu',
        }

        // when
        const wrapper = shallow(<NotificationV1 {...props} />)
        const link = wrapper.find('a')
        const icon = wrapper.find(Icon)
        const firstDiv = wrapper.find('div').at(0)
        const button = wrapper.find('button')

        // then
        expect(icon).toHaveLength(1)
        expect(firstDiv.prop('className')).toBe('notification is-info')
        expect(icon.prop('png')).toBe('picto-info-solid-blue-S')
        expect(link.props().href).toStrictEqual(props.notification.url)
        expect(link.text()).toStrictEqual(props.notification.urlLabel)
        expect(button.text()).toStrictEqual('Fermer')
      })
      it('should close notification popup when clicking on button', () => {
        // given
        props.notification = {
          tag: 'offerers',
          text:
            'Commencez par créer un lieu pour accueillir vos offres physiques (événements, livres, abonnements…)',
          type: 'info',
          url: '/structures/AFPQ/lieux/creation',
          urlLabel: 'Nouveau lieu',
        }

        // when
        const wrapper = shallow(<NotificationV1 {...props} />)
        wrapper.find('button').simulate('click')
        const expected = { type: 'CLOSE_NOTIFICATION' }

        // then
        expect(props.dispatch).toHaveBeenCalledWith(expected)
      })
    })

    describe('tooltip notification', () => {
      it('should render a tooltip with proper informations when tooltip is provided', () => {
        // given
        props.notification = {
          type: 'tip',
          tooltip: {
            place: 'bottom',
            tip:
              '<p>Il n’est pas possible de modifier le nom, l’addresse et la géolocalisation du lieu quand un siret est renseigné.</p>',
            type: 'info',
          },
        }

        // when
        const wrapper = shallow(<NotificationV1 {...props} />)
        const icon = wrapper.find(Icon)
        const spans = wrapper.find('span')
        const button = wrapper.find('button')

        // then
        expect(button).toHaveLength(0)
        expect(icon.prop('svg')).toBe('picto-tip')
        expect(spans.at(1).prop('data-tip')).toStrictEqual(props.notification.tooltip.tip)
      })
    })
  })
})
