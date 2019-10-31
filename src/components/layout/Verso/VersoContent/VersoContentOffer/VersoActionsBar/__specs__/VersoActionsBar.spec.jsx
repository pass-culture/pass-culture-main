import VersoActionsBar from '../VersoActionsBar'
import { shallow } from 'enzyme'
import React from 'react'

describe('src | components | layout | Verso | VersoContentOffer | VersoActionsBar', () => {
  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<VersoActionsBar />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  it('should render a link with the right props', () => {
    // when
    const wrapper = shallow(<VersoActionsBar />)

    // then
    const link = wrapper.find('a')
    expect(link).toHaveLength(1)
    expect(link.prop('className')).toStrictEqual(
      'is-red-text is-bold flex-columns items-center flex-center'
    )
    expect(link.prop('href')).toBeNull()
    expect(link.prop('id')).toStrictEqual('verso-online-booked-button')
    expect(link.prop('rel')).toStrictEqual('noopener noreferrer')
    expect(link.prop('target')).toStrictEqual('_blank')
  })
})
