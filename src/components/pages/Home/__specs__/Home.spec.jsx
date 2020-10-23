import { shallow } from 'enzyme'
import React from 'react'

import Main from 'components/layout/Main'

import Card from '../Card/Card'
import Home from '../Home'

describe('src | components | Home', () => {
  it('should render two Cards', () => {
    // when
    const wrapper = shallow(<Home />)

    // then
    const mainComponent = wrapper.find(Main)
    const cards = wrapper.find(Card)

    expect(mainComponent).toHaveLength(1)
    expect(mainComponent.prop('name')).toStrictEqual('home')
    expect(mainComponent.prop('whiteHeader')).toStrictEqual(true)

    expect(cards).toHaveLength(2)
    expect(cards.at(0).props()).toStrictEqual({
      navLink: '/guichet',
      svg: 'ico-guichet-w',
      text: 'Enregistrez les codes de réservation des porteurs du Pass.',
      title: 'Guichet',
    })
    expect(cards.at(1).props()).toStrictEqual({
      navLink: '/offres',
      svg: 'ico-offres-w',
      text: 'Créez et mettez en avant vos offres présentes sur le Pass.',
      title: 'Offres',
    })
  })
})
