// $(yarn bin)/jest --env=jsdom ./src/components/verso/verso-controls/wallet/tests/VersoWallet.spec.js --watch
import React from 'react'
import { shallow } from 'enzyme'
import VersoWallet from '../VersoWallet'

describe('src | components | verso | verso-controls | wallet | VersoWallet', () => {
  it('should match snapshot', () => {
    // given
    const props = { value: 10 }
    // when
    const wrapper = shallow(<VersoWallet {...props} />)
    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })
  it('should contains elements with matching text', () => {
    // given
    const props = { value: 10 }
    // when
    const wrapper = shallow(<VersoWallet {...props} />)
    // then
    expect(wrapper.prop('id')).toEqual('verso-wallet')
    // then
    const label = wrapper.find('#verso-wallet-label')
    expect(label).toHaveLength(1)
    expect(label.text()).toEqual('Mon Pass')
    // then
    const value = wrapper.find('#verso-wallet-value')
    expect(value).toHaveLength(1)
    expect(value.text()).toEqual(`${props.value}\u00a0€`)
  })
})
