import React from 'react'
import { shallow } from 'enzyme'
import TiteLiveInformation from '../TiteLiveInformation'

describe('src | components | pages | Offer | TiteLiveInformation | TiteLiveInformation', () => {
  let props

  beforeEach(() => {
    props = {
      offererId: 'ABCD',
      thumbUrl: 'http://localhost/storage/thumbs/products/AERTR',
      venueId: 'EARZ',
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<TiteLiveInformation {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    it('should render a link to venue page', () => {
      // when
      const wrapper = shallow(<TiteLiveInformation {...props} />)

      // then
      const link = wrapper.find('span')
      expect(link).toHaveLength(1)
      expect(link.prop('className')).toBe('button')
      expect(link.prop('data-tip')).toContain("<a href='/structures/ABCD/lieux/EARZ'>")
    })
  })
})
