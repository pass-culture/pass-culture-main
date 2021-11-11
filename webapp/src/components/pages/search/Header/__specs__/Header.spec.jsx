import { mount, shallow } from 'enzyme'
import React from 'react'
import Header from '../Header'

describe('search header', () => {
  let props
  beforeEach(() => {
    props = {
      onSearchChange: jest.fn(),
      onResetClick: jest.fn(),
      onSubmit: jest.fn(),
    }
  })

  it('should display button to reinitialize search when able to go back', () => {
    // given
    props = {
      ...props,
      onBackButtonClick: jest.fn(),
    }

    // when
    const wrapper = mount(<Header {...props} />)

    // then
    const backButton = wrapper.find('button').at(0)
    const backImage = wrapper.find('img[alt="Réinitialiser la recherche"]')
    expect(backButton).toHaveLength(1)
    expect(backImage).toHaveLength(1)
  })

  it('should call function when clicking on back button', () => {
    // given
    props = {
      ...props,
      onBackButtonClick: jest.fn(),
    }
    const wrapper = shallow(<Header {...props} />)

    // when
    const backButton = wrapper.find('button').at(0)
    backButton.invoke('onClick')()

    // then
    expect(props.onBackButtonClick).toHaveBeenCalledTimes(1)
  })

  it('should call a function when something is typed in input field', () => {
    // given
    const wrapper = shallow(<Header {...props} />)

    // when
    const input = wrapper.find('input')
    input.invoke('onChange')({ target: { value: 'recherche' } })

    // then
    expect(props.onSearchChange).toHaveBeenCalledTimes(1)
  })

  it('should call function when form is submitted', () => {
    // given
    const wrapper = shallow(<Header {...props} />)

    // when
    const form = wrapper.find('form')
    form.invoke('onSubmit')({
      target: { keywords: { value: 'recherche' } },
      preventDefault: jest.fn(),
    })

    // then
    expect(props.onSubmit).toHaveBeenCalledTimes(1)
  })

  describe('reset cross', () => {
    it('should not display reset cross when nothing is typed in text input', () => {
      // when
      const wrapper = shallow(<Header {...props} />)

      // then
      const resetButton = wrapper.find('button[type="reset"]')
      expect(resetButton).toHaveLength(0)
    })

    it('should display reset cross when prop value is not empty', () => {
      // given
      props.value = 'tortue'

      // when
      const wrapper = shallow(<Header {...props} />)

      // then
      const resetButton = wrapper.find('button[type="reset"]')
      expect(resetButton).toHaveLength(1)
    })

    it('should call a function when clicking on reset cross', () => {
      // given
      props = {
        ...props,
        onResetClick: jest.fn(),
        value: 'tortue',
      }
      const wrapper = shallow(<Header {...props} />)

      const resetButton = wrapper.find('button[type="reset"]')

      // when
      resetButton.invoke('onClick')()

      // then
      expect(props.onResetClick).toHaveBeenCalledTimes(1)
    })
  })
})
