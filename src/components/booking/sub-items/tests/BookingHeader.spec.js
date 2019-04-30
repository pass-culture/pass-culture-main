import React from 'react'
import { shallow } from 'enzyme'

import BookingHeader from '../BookingHeader'

describe('src | components | booking | BookingHeader', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      const props = {
        recommendation: {
          offer: {
            eventOrThing: { name: 'Titre de eventorthing' },
            name: 'Titre de la recommendation',
            venue: { name: 'Titre de la venue ' },
          },
        },
      }
      const wrapper = shallow(<BookingHeader {...props} />)
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
