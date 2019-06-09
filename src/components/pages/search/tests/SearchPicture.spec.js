import { shallow } from 'enzyme'
import React from 'react'

import { SearchPicture } from '../SearchPicture'

describe('src | components | pages | search | SearchPicture', () => {
  let props

  beforeEach(() => {
    props = {
      category: 'Écouter',
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<SearchPicture {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  describe('render()', () => {
    it('should display image with the right url by default', () => {
      // given
      const wrapper = shallow(<SearchPicture {...props} />)

      // when
      const img = wrapper.find('img').props()

      // then
      expect(img.src).toBe('http://localhost/icons/img-Écouter.png')
      expect(img.alt).toBe('Rechercher des offres de type Écouter')
    })
  })
})
