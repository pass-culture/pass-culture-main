import React from 'react'
import { shallow } from 'enzyme'

import SearchPicture from '../SearchPicture'

describe('src | components | pages | search | SearchPicture', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        searchType: 'Écouter',
      }

      // when
      const wrapper = shallow(<SearchPicture {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
  describe('render', () => {
    it('should display image with the right url', () => {
      // given
      const props = {
        searchType: 'Écouter',
      }

      // when
      const wrapper = shallow(<SearchPicture {...props} />)
      const img = wrapper.find('img').props()

      // then
      expect(img.src).toEqual('http://localhost/icons/img-Ecouter.png')
      expect(img.alt).toEqual('Rechercher des offres de type Écouter')
    })
  })
})
