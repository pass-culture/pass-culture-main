import { shallow } from 'enzyme'
import React from 'react'

import { ROOT_PATH } from '../../../../utils/config'
import { NavResultsHeader } from '../NavResultsHeader'

describe('src | components | pages | search | NavResultsHeader', () => {
  let props

  beforeEach(() => {
    props = {
      category: 'Applaudir',
      description:
        'Voulez-vous suivre un géant de 12 mètres dans la ville ? Rire devant un seul-en-scène ? Rêver le temps d’un opéra ou d’un spectacle de danse, assister à une pièce de théâtre, ou vous laisser conter une histoire ?',
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<NavResultsHeader {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  describe('render()', () => {
    it('should display the background image with the right description by default', () => {
      // given
      props.category = 'Écouter'
      props.description = 'Lorem Ipsum'
      const wrapper = shallow(<NavResultsHeader {...props} />)

      // when
      const img = wrapper.find('#nav-results-header').props()

      // then
      const imgUrl = `${ROOT_PATH}/icons/img-Écouter-L.jpg`
      expect(img.style.backgroundImage).toBe(`url(${imgUrl})`)
      expect(img.title).toBe('Liste des offres de type Écouter')
    })
  })
})
