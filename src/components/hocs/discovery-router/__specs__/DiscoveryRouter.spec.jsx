import React from 'react'
import { shallow } from 'enzyme'

import DiscoveryRouter from '../DiscoveryRouter'
import DiscoveryContainerV1 from '../../../pages/discovery-v1/DiscoveryContainer'

describe('discoveryRouter', () => {
  it('should load discovery v1 component', () => {
    // when
    const wrapper = shallow(<DiscoveryRouter />)

    // then
    expect(wrapper.find(DiscoveryContainerV1)).toHaveLength(1)
  })
})
