import React from 'react'
import { shallow } from 'enzyme'
import VersoWallet from '../VersoWallet'

describe('src | components | verso | verso-controls | wallet | VersoWallet', () => {
  it('should match snapshot', () => {
    // given
    const props = { value: 10 }

    // when
    const wrapper = shallow(<VersoWallet {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  it('wallet display should exists', () => {
    // given
    const props = { value: 10 }

    // when
    const wrapper = shallow(<VersoWallet {...props} />)

    // then
    expect(wrapper.prop('id')).toStrictEqual('verso-wallet')
  })

  it('wallet display should have a label', () => {
    // given
    const props = { value: 10 }
    // when
    const wrapper = shallow(<VersoWallet {...props} />)
    const label = wrapper.find('#verso-wallet-label')

    // then
    expect(label).toHaveLength(1)
    expect(label.text()).toStrictEqual('Mon pass')
  })

  it('wallet display should show a price', () => {
    // given
    const props = { value: 10 }

    // when
    const wrapper = shallow(<VersoWallet {...props} />)
    const value = wrapper.find('#verso-wallet-value')

    // then
    expect(value).toHaveLength(1)
    expect(value.text()).toStrictEqual(`${props.value}\u00a0€`)
  })
})
