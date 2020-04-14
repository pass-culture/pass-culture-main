import { shallow } from 'enzyme'
import React from 'react'
import Icon from '../../../../layout/Icon/Icon'
import { EmptySearchResult } from '../EmptySearchResult'

describe('components | EmptySearchResult', () => {
  it('should display an image of empty search results', () => {
    // When
    const wrapper = shallow(
      <EmptySearchResult
        onNewSearchAroundMe={jest.fn()}
        searchedKeywords="mots clés recherchés"
      />
    )

    // Then
    const image = wrapper.find(Icon)
    expect(image).toHaveLength(1)
    expect(image.prop('svg')).toBe('ico-no-offer')
  })

  it('should display searched keywords', () => {
    // When
    const wrapper = shallow(
      <EmptySearchResult
        onNewSearchAroundMe={jest.fn()}
        searchedKeywords="mots clés recherchés"
      />
    )

    // Then
    const searchedKeywords = wrapper.find({
      children: '"mots clés recherchés"',
    })
    expect(searchedKeywords).toHaveLength(1)
  })

  it('should call onNewSearchAroundMe on button click', () => {
    // Given
    const onNewSearchAroundMe = jest.fn()
    const wrapper = shallow(
      <EmptySearchResult
        onNewSearchAroundMe={onNewSearchAroundMe}
        searchedKeywords="mots clés recherchés"
      />
    )

    // When
    wrapper.find({ children: 'autour de chez toi' }).simulate('click')

    // Then
    expect(onNewSearchAroundMe).toHaveBeenCalledTimes(1)
  })
})
