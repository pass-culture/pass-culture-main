import React from 'react'
import StockInformationMessage from '../StockInformationMessage'
import { shallow } from 'enzyme'

describe('src | components | pages | StocksManager | utils | StockInformationMessage', () => {
  it('should return correct message when provider is Allociné', () => {
    // given
    const providerName = 'Allociné'

    // when
    const stockInformationMessage = shallow(<StockInformationMessage providerName={providerName} />)

    // then
    expect(stockInformationMessage.text()).toBe('Il n’est pas possible d’ajouter d’horaires pour cet événement Allociné')
  })

  it('should return correct message when provider is not Allociné', () => {
    // given
    const providerName = 'Libraires'

    // when
    const stockInformationMessage = shallow(<StockInformationMessage providerName={providerName} />)

    // then
    expect(stockInformationMessage.text()).toBe('Il n’est pas possible d’ajouter ni de supprimer d’horaires pour cet événement Libraires')
  })
})
