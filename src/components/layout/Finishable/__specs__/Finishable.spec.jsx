import { shallow } from 'enzyme'
import React from 'react'

import Finishable from '../Finishable'
import Icon from '../../Icon/Icon'

describe('components | Finishable', () => {
  let props

  beforeEach(() => {
    props = {
      children: <p>
        {'Cette offre n’est pas terminée'}
      </p>,
    }
  })

  describe('when the offer is bookable', () => {
    it('should not render the ribbon', () => {
      // given
      props.offerCanBeBooked = true

      // when
      const wrapper = shallow(<Finishable {...props} />)

      // then
      expect(wrapper.find(Icon)).toHaveLength(0)
    })
  })

  describe('when the offer is not bookable', () => {
    it('should render the ribbon', () => {
      // given
      props.offerCanBeBooked = false

      // when
      const wrapper = shallow(<Finishable {...props} />)

      // then
      const icon = wrapper.find(Icon)
      expect(icon).toHaveLength(1)
      expect(icon.prop('alt')).toBe('Réservation finie')
      expect(icon.prop('className')).toBe('finishable-ribbon-img')
      expect(icon.prop('svg')).toBe('badge-termine')
    })
  })
})
