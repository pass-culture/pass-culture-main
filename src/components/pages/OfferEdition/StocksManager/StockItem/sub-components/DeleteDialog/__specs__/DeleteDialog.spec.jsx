import { shallow } from 'enzyme'
import React from 'react'

import DeleteDialog from '../DeleteDialog'

describe('src | components | pages | Offer | StockItem | DeleteDialog', () => {
  describe('snapshot', () => {
    it('should match the snapshot when isEvent = true', () => {
      // given
      const initialProps = {
        isEvent: true,
      }

      // when
      const wrapper = shallow(<DeleteDialog {...initialProps} />)

      // then
      expect(wrapper).toMatchSnapshot()
    })

    it('should match the snapshot when isEvent = false', () => {
      // given
      const initialProps = {
        isEvent: false,
      }

      // when
      const wrapper = shallow(<DeleteDialog {...initialProps} />)

      // then
      expect(wrapper).toMatchSnapshot()
    })
  })
})
