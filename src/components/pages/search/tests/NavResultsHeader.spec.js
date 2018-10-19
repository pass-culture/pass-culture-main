import React from 'react'
import { shallow } from 'enzyme'

import NavResultsHeader from '../NavResultsHeader'

import { ROOT_PATH } from '../../../../utils/config'

describe('src | components | pages | search | NavResultsHeader', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        category: 'Applaudir',
        description:
          'Voulez-vous suivre un géant de 12 mètres dans la ville ? Rire devant un seul-en-scène ? Rêver le temps d’un opéra ou d’un spectacle de danse, assister à une pièce de théâtre, ou vous laisser conter une histoire ?',
        sublabel: 'Applaudir',
      }

      // when
      const wrapper = shallow(<NavResultsHeader {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
  describe('render', () => {
    it('should display the background image with the right description', () => {
      // given
      const props = {
        category: 'Écouter',
        description: 'Lorem Ipsum',
      }

      // when
      const wrapper = shallow(<NavResultsHeader {...props} />)
      const img = wrapper.find('#nav-results-header').props()
      //
      // // then
      const imgUrl = `${ROOT_PATH}/icons/img-Écouter-L.jpg`
      expect(img.style.backgroundImage).toEqual(`url(${imgUrl})`)
      expect(img.title).toEqual('Liste des offres de type Écouter')
    })
  })
})
