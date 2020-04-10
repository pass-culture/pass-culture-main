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
})
