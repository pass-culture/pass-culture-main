import React from 'react'
import { shallow } from 'enzyme'

import SearchFilter from '../SearchFilter'

describe('src | components | pages | search | SearchFilter', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        filterIsVisible: true,
        pagination: {
          windowQuery: {
            categories: null,
            date: '2018-09-28T12:52:52.341Z',
            distance: '50',
            jours: '0-1',
            latitude: '48.8637546',
            longitude: '2.337428',
            [`mots-cles`]: 'fake',
            orderBy: 'offer.id+desc',
          },
        },
      }

      // when
      const wrapper = shallow(<SearchFilter {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
