import { mount } from 'enzyme'
import React from 'react'

import Select from '../Select'

describe('src | components | layout | form | Select', () => {
  let props
  beforeEach(() => {
    props = {
      defaultOption: { displayName: 'Option par défaut', id: 'all' },
      handleSelection: jest.fn(),
      isDisabled: false,
      label: 'Label de mon select',
      name: 'items-select',
      options: [
        { displayName: 'Ma première option', id: '1' },
        { displayName: 'Ma deuxième option', id: '2' },
      ],
      selectedValue: 'all',
    }
  })

  it('should render a select input with the provided default value', async () => {
    // given
    props.options = []

    // when
    const wrapper = await mount(<Select {...props} />)

    // then
    const select = wrapper.find('select').at(0)
    const options = select.find('option')
    expect(options).toHaveLength(1)
    expect(options.at(0).text()).toBe(props.defaultOption.displayName)
  })

  it('should render a select input containing given options in given order', async () => {
    // when
    const wrapper = await mount(<Select {...props} />)

    // then
    const select = wrapper.find('select').at(0)
    const options = select.find('option')
    expect(options).toHaveLength(3)
    expect(options.at(1).text()).toBe(props.options[0].displayName)
    expect(options.at(2).text()).toBe(props.options[1].displayName)
  })

  it('should have given option selected when value is given', async () => {
    // given
    props.selectedValue = props.options[0].id

    // when
    const wrapper = await mount(<Select {...props} />)

    // then
    const select = wrapper.find('select').at(0)
    expect(select.props().value).toBe(props.options[0].id)
  })

  it('should call callback on blur', async () => {
    // given
    const selectedOption = { target: { value: '1' } }
    const wrapper = await mount(<Select {...props} />)
    const select = wrapper.find('select')

    // when
    await select.invoke('onBlur')(selectedOption)

    // then
    const handleSelectionParameters = props.handleSelection.mock.calls[0][0]
    expect(handleSelectionParameters.target).toBe(selectedOption.target)
  })

  it('should call callback on change', async () => {
    // given
    const selectedOption = { target: { value: '1' } }
    const wrapper = await mount(<Select {...props} />)
    const select = wrapper.find('select')

    // when
    await select.invoke('onChange')(selectedOption)

    // then
    const handleSelectionParameters = props.handleSelection.mock.calls[0][0]
    expect(handleSelectionParameters.target).toBe(selectedOption.target)
  })
})
