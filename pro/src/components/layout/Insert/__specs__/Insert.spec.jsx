import { mount, shallow } from 'enzyme'

import Insert from '../Insert'
import React from 'react'

describe('src | components | layout | Insert', () => {
  let props

  beforeEach(() => {
    props = {
      children: `{'Les'}
        <b>
          {' réservations d’évènements '}
        </b>
        {'sont annulables par les utilisateurs jusqu’à 72h avant la date d’évènement.'}
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
          {' réservations d’évènements '}
        </b>
        {'sont annulables par les utilisateurs jusqu’à 72h avant la date d’évènement.'}
        <p />
        <p />
        {'La contremarque ne peut être validée qu’après ce délai.'}`
      expect(span.text()).toBe(expected)
    })
  })
})
