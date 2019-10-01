import React from 'react'
import { shallow } from 'enzyme'

import OfferPreviewLink from '../OfferPreviewLink'

describe('src | components | layout | OfferPreviewLink', () => {
  let props

  beforeEach(() => {
    props = {
      className: 'Fake className',
      offerWebappUrl: 'fake url',
      onClick: jest.fn()
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<OfferPreviewLink {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    describe('a link', () => {
      it('should display correct text and className', () => {
        // given

        // when
        const wrapper = shallow(<OfferPreviewLink {...props} />)
        const link = wrapper.find('a')
        const mainDiv = wrapper.find('div')

        // then
        expect(link).toHaveLength(1)
        expect(mainDiv.prop('className')).toBe('Fake className')
        expect(link.text()).toStrictEqual( "<Icon />Prévisualiser")
      })

      it('should call a function that open an new window on clicking', () => {
        // given
        const wrapper = shallow(<OfferPreviewLink {...props} />)

        // when
        wrapper.find('a').simulate('click')

        // then
        expect(props.onClick).toHaveBeenCalledWith()
      })
    })

    describe('icon', () => {
      it('should display correct icon type', () => {
        // given
        const wrapper = shallow(<OfferPreviewLink {...props} />)

        // when
        const icon = wrapper.find('Icon')

        // then
        expect(icon).toHaveLength(1)
        expect(icon.prop('svg')).toBe('ico-eye')
      })
    })
  })
})
