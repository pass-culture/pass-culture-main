import React from 'react'
import { shallow } from 'enzyme'

import VersoContentTuto from '../VersoContentTuto'
import { THUMBS_URL } from '../../../../utils/config'

describe('src | components | verso | verso-content | VersoContentTuto', () => {
  it('should match snapshot', () => {
    // given
    const props = { mediationId: '1234' }

    // when
    const wrapper = shallow(<VersoContentTuto {...props} />)
    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  it('should have a classnamed element with sourced img', () => {
    // given
    const mediationId = '1234'
    const props = { mediationId }
    const url = `${THUMBS_URL}/mediations/${mediationId}_1`

    // when
    const wrapper = shallow(<VersoContentTuto {...props} />)

    // then
    const img = wrapper.find('img')
    expect(img).toHaveLength(1)
    expect(img.hasClass('verso-tuto-mediation')).toBe(true)
    expect(img.prop('alt')).toBe('verso')
    expect(img.prop('src')).toEqual(url)
  })
})
