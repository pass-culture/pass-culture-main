import React from 'react'
import { shallow } from 'enzyme'

import DiscoveryRouter from '../DiscoveryRouter'
import DiscoveryContainer from '../../../pages/discovery/DiscoveryContainer'
import DiscoveryContainerV2 from '../../../pages/discovery-v2/DiscoveryContainer'

describe('discoveryRouter', () => {
  describe('when discovery v2 feature flipping is active', () => {
    it('should load discovery v2 component', () => {
      // given
      const props = {
        isDiscoveryV2Active: true,
      }

      // when
      const wrapper = shallow(<DiscoveryRouter {...props} />)

      // then
      expect(wrapper.find(DiscoveryContainerV2)).toHaveLength(1)
    })
  })

  describe('when discovery v2 feature flipping is deactive', () => {
    it('should load discovery v1 component', () => {
      // given
      const props = {
        isDiscoveryV2Active: false,
      }

      // when
      const wrapper = shallow(<DiscoveryRouter {...props} />)

      // then
      expect(wrapper.find(DiscoveryContainer)).toHaveLength(1)
    })
  })
})
