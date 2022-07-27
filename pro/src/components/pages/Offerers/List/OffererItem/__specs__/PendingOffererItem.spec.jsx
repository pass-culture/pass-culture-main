import { shallow } from 'enzyme'
import React from 'react'

import PendingOffererItem from '../PendingOffererItem'

describe('src | components | pages | Offerers | OffererItem | PendingOffererItem', () => {
  let props

  beforeEach(() => {
    props = {
      offerer: {},
    }
  })

  it('should display sentences', () => {
    // when
    const wrapper = shallow(<PendingOffererItem {...props} />)

    // then
    const sentence1 = wrapper.find('p')
    const sentence2 = wrapper.find({
      children: 'Rattachement en cours de validation',
    })
    expect(sentence1.at(0).text()).toBe(' (SIREN: )')
    expect(sentence2).toHaveLength(1)
  })
})
