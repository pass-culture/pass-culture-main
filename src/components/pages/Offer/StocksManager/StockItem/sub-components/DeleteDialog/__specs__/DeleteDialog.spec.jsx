import { shallow } from 'enzyme'
import React from 'react'

import DeleteDialog from '../DeleteDialog'

describe('src | components | pages | Offer | StockItem | DeleteDialog', () => {
  it('should display sentence and buttons when isEvent = true', () => {
    // given
    const initialProps = {
      isEvent: true,
    }

    // when
    const wrapper = shallow(<DeleteDialog {...initialProps} />)

    // then
    const td = wrapper.find('td')
    expect(td.at(0).text()).toBe('En confirmant l’annulation de cette date, vous supprimerez aussi toutes les réservations associées. Êtes-vous sûr de vouloir continuer ?')
    expect(td.at(1).find('button').find({ children: 'Oui' })).toHaveLength(1)
    expect(td.at(2).find('button').find({ children: 'Non' })).toHaveLength(1)
  })

  it('should display sentence and buttons when isEvent = false', () => {
    // given
    const initialProps = {
      isEvent: false,
    }

    // when
    const wrapper = shallow(<DeleteDialog {...initialProps} />)

    // then
    const td = wrapper.find('td')
    expect(td.at(0).text()).toBe('En confirmant l’annulation de ce stock, vous supprimerez aussi toutes les réservations associées. Êtes-vous sûr de vouloir continuer ?')
    expect(td.at(1).find('button').find({ children: 'Oui' })).toHaveLength(1)
    expect(td.at(2).find('button').find({ children: 'Non' })).toHaveLength(1)
  })
})
