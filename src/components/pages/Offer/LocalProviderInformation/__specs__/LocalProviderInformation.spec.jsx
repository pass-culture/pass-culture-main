import React from 'react'
import { shallow } from 'enzyme'
import LocalProviderInformation from '../LocalProviderInformation'
import Thumb from '../../../../layout/Thumb'

describe('src | LocalProviderInformationContainer', () => {
  let props

  beforeEach(() => {
    props = {
      offererId: 'ABCD',
      offerName: 'Super Livre',
      providerInfo: {
        icon: 'TiteliveStocks',
        name: 'Tite live',
      },
      thumbUrl: 'http://localhost/storage/thumbs/products/AERTR',
      venueId: 'EARZ',
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<LocalProviderInformation {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    it('should render a link to venue page', () => {
      // when
      const wrapper = shallow(<LocalProviderInformation {...props} />)

      // then
      const link = wrapper.find('span')
      expect(link).toHaveLength(1)
      expect(link.prop('className')).toBe('button')
      expect(link.prop('data-tip')).toContain("<a href='/structures/ABCD/lieux/EARZ'>")
    })

    it('should render thumb alternate description with product name', () => {
      // when
      const wrapper = shallow(<LocalProviderInformation {...props} />)

      // then
      const thumb = wrapper.find(Thumb)
      expect(thumb).toHaveLength(1)
      expect(thumb.prop('alt')).toBe('couverture du livre Super Livre')
      expect(thumb.prop('src')).toBe('http://localhost/storage/thumbs/products/AERTR')
    })
  })
})
