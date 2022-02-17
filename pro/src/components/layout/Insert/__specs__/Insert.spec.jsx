import { mount, shallow } from 'enzyme'
import React from 'react'

import Insert from '../Insert'

describe('src | components | layout | Insert', () => {
  let props

  beforeEach(() => {
    props = {
      children: `{'Les'}
        <b>
          {' réservations d’événements '}
        </b>
        {'sont annulables par les utilisateurs jusqu’à 72h avant la date d’événement.'}
        <p />
        <p />
        {'La contremarque ne peut être validée qu’après ce délai.'}`,
      icon: 'example-icon-name',
    }
  })

  describe('render', () => {
    it('should render an Icon', () => {
      // when
      const wrapper = shallow(<Insert {...props} />)

      // then
      const icon = wrapper.find('Icon')
      expect(icon).toHaveLength(1)
    })

    it('should render a children', () => {
      // when
      const wrapper = mount(<Insert {...props} />)

      // then
      const span = wrapper.find('span')
      const expected = `{'Les'}
        <b>
          {' réservations d’événements '}
        </b>
        {'sont annulables par les utilisateurs jusqu’à 72h avant la date d’événement.'}
        <p />
        <p />
        {'La contremarque ne peut être validée qu’après ce délai.'}`
      expect(span.text()).toBe(expected)
    })
  })
})
