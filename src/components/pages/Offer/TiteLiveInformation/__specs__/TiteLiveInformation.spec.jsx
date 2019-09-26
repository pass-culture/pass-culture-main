import React from 'react'
import { shallow } from 'enzyme'
import TiteLiveInformation from '../TiteLiveInformation'
import Thumb from '../../../../layout/Thumb'

describe('src | components | pages | Offer | TiteLiveInformation | TiteLiveInformation', () => {
  let props

  beforeEach(() => {
    props = {
      offererId: 'ABCD',
      productName: 'Super Livre',
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

    it('should render thumb alternate description with product name', () => {
      // when
      const wrapper = shallow(<TiteLiveInformation {...props} />)

      // then
      const link = wrapper.find(Thumb)
      expect(link).toHaveLength(1)
      expect(link.prop('alt')).toBe('couverture du livre Super Livre')
      expect(link.prop('src')).toBe('http://localhost/storage/thumbs/products/AERTR')
    })
  })
})
