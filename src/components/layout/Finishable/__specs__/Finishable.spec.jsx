import { shallow } from 'enzyme'
import React from 'react'

import Finishable from '../Finishable'

describe('src | components | layout | Finishable | Finishable', () => {
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
      props.isNotBookable = false

      // when
      const wrapper = shallow(<Finishable {...props} />)

      // then
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('when the offer is not bookable', () => {
    it('should render the ribbon', () => {
      // given
      props.isNotBookable = true

      // when
      const wrapper = shallow(<Finishable {...props} />)

      // then
      expect(wrapper).toMatchSnapshot()
    })
  })
})
