import React from 'react'
import { shallow } from 'enzyme'
import BankInformation from '../BankInformation'
import { Offerer } from '../../Offerer'

describe('src | components | pages | Offerer | BankInformation ', () => {
  const offerer = new Offerer({
    id: 'AA',
    name: 'fake offerer name',
    address: 'fake address',
    bic: 'ABC',
    iban: 'DEF',
  })

  let props
  beforeEach(() => {
    props = { offerer }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<BankInformation {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  it('should render instruction block information are not provided', () => {
    // Given
    const offererWithoutBI = new Offerer({
      id: 'AA',
      name: 'fake offerer name',
      address: 'fake address',
      bic: null,
      iban: null,
    })

    // when
    const wrapper = shallow(<BankInformation
      {...props}
      offerer={offererWithoutBI}
                            />)

    // then
    const bankInstructions = wrapper.find('.bi-instructions')
    expect(bankInstructions).toHaveLength(1)
    expect(bankInstructions.text()).toBe(
      'Renseigner vos coordonnées bancaires pour être remboursé de vos offres éligibles'
    )
  })

  it('should not render instruction block information are provided', () => {
    // when
    const wrapper = shallow(<BankInformation {...props} />)

    // then
    const bankInstructions = wrapper.find('.bi-instructions')
    expect(bankInstructions).toHaveLength(0)
  })
})
