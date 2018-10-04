import React from 'react'
import { shallow } from 'enzyme'

import NavResultsHeader from '../NavResultsHeader'

describe.skip('src | components | pages | search | NavResultsHeader', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        searchType: 'Écouter',
        typeSublabels: {
          description:
            'Voulez-vous suivre un géant de 12 mètres dans la ville ? Rire devant un seul-en-scène ? Rêver le temps d’un opéra ou d’un spectacle de danse, assister à une pièce de théâtre, ou vous laisser conter une histoire ?',
          sublabel: 'Applaudir',
        },
      }

      // when
      const wrapper = shallow(<NavResultsHeader {...props} />)

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
      const wrapper = shallow(<NavResultsHeader {...props} />)
      const img = wrapper.find('img').props()

      // then
      expect(img.src).toEqual('http://localhost/icons/img-Ecouter.png')
      expect(img.alt).toEqual('Rechercher des offres de type Écouter')
    })
  })
})
