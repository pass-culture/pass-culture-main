import { shallow } from 'enzyme'
import React from 'react'

import OfferPreviewLink from '../OfferPreviewLink'

describe('src | components | layout | OfferPreviewLink', () => {
  let props

  beforeEach(() => {
    props = {
      className: 'Fake className',
      offerWebappUrl: 'fake url',
      onClick: jest.fn(),
    }
  })

  describe('render', () => {
    describe('a link', () => {
      it('should display correct text and className', () => {
        // given
        const wrapper = shallow(<OfferPreviewLink {...props} />)

        // when
        const link = wrapper.find('a')

        // then
        expect(link).toHaveLength(1)
        expect(link.prop('className')).toBe('Fake className')
        expect(link.text()).toStrictEqual('<Icon />Prévisualiser')
      })

      it('should execute the onClick property with the link is clicked', () => {
        // given
        const wrapper = shallow(
          <div>
            <OfferPreviewLink {...props} />
          </div>
        )

        // when
        wrapper.find('OfferPreviewLink').simulate('click')

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
