import { shallow } from 'enzyme'
import React from 'react'

import Thumb from '../../../../layout/Thumb'
import LocalProviderInformation from '../LocalProviderInformation'

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
      expect(thumb.prop('url')).toBe('http://localhost/storage/thumbs/products/AERTR')
    })
  })
})
