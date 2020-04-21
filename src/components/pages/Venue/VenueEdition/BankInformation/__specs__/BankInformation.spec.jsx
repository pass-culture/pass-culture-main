import React from 'react'
import { shallow } from 'enzyme'
import BankInformation from '../BankInformation'

describe('src | components | pages | Venue | BankInformation ', () => {
  const venue = {
    id: 'AA',
    name: 'fake venue name',
    bic: 'ABC',
    iban: 'DEF',
  }

  let props
  beforeEach(() => {
    props = { venue }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<BankInformation {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  it('should render instruction block when bancking information are not provided', () => {
    // Given
    const venue = {
      id: 'AA',
      name: 'fake venue name',
      bic: null,
      iban: null,
    }

    // when
    const wrapper = shallow(<BankInformation {...props} venue={venue} />)

    // then
    const bankInstructions = wrapper.find({
      children: 'Renseigner vos coordonnées bancaires pour être remboursé de vos offres éligibles',
    })
    expect(bankInstructions).toHaveLength(1)
  })

  it('should not render instruction block when BIC and IBAN are provided', () => {
    // when
    const wrapper = shallow(<BankInformation {...props} />)

    // then
    const bankInstructions = wrapper.find({
      children: 'Renseigner vos coordonnées bancaires pour être remboursé de vos offres éligibles',
    })
    expect(bankInstructions).toHaveLength(0)
  })
})
