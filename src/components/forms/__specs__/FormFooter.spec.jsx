import React from 'react'
import { mount, shallow } from 'enzyme'
import { MemoryRouter } from 'react-router'

import FormFooter from '../FormFooter'
import { Link } from 'react-router-dom'

describe('components | FormFooter', () => {
  describe('render', () => {
    describe('regular links', () => {
      it('should render a Link component when an url is provided', () => {
        // given
        const props = {
          cancel: null,
          className: null,
          items: [
            {
              className: 'my-class',
              disabled: false,
              id: 'my-id',
              label: 'my-label',
              url: 'my-url',
            },
          ],
        }

        // when
        const wrapper = shallow(<FormFooter {...props} />)

        // then
        const regularLink = wrapper.find(Link)
        expect(regularLink).toHaveLength(1)
        expect(regularLink.props()).toStrictEqual({
          children: 'my-label',
          className: 'my-class',
          disabled: false,
          id: 'my-id',
          onClick: undefined,
          onKeyPress: undefined,
          to: 'my-url',
        })
      })

      it('should trigger tracker event when click on link when provided', () => {
        // given
        const trackerMock = jest.fn()
        const props = {
          cancel: null,
          className: null,
          items: [
            {
              className: 'my-class',
              id: 'my-id',
              label: 'my-label',
              tracker: trackerMock,
              url: 'my-url',
            },
          ],
        }
        const wrapper = mount(
          <MemoryRouter>
            <FormFooter {...props} />
          </MemoryRouter>
        )
        const regularLink = wrapper.find('a[id="my-id"]')

        // when
        regularLink.invoke('onClick')({})

        // then
        expect(trackerMock).toHaveBeenCalledTimes(1)
      })

      it('should render a cancel link when a cancel url is provided', () => {
        // given
        const props = {
          items: [
            {
              className: 'my-class',
              disabled: false,
              id: 'my-id',
              label: 'my-label',
              url: 'my-url',
            },
          ],
          className: null,
        }

        // when
        const wrapper = shallow(<FormFooter {...props} />)

        // then
        const cancelLink = wrapper.find(Link)
        expect(cancelLink).toHaveLength(1)
        expect(cancelLink.props()).toStrictEqual({
          children: 'my-label',
          className: 'my-class',
          disabled: false,
          id: 'my-id',
          onClick: undefined,
          onKeyPress: undefined,
          to: 'my-url',
        })
      })
    })

    describe('buttons', () => {
      it('should render a submit button when an url is not provided', () => {
        // given
        const props = {
          cancel: null,
          className: null,
          items: [
            {
              className: 'my-class',
              disabled: false,
              id: 'my-id',
              label: 'my-label',
            },
          ],
        }

        // when
        const wrapper = shallow(<FormFooter {...props} />)

        // then
        const submitButton = wrapper.find('button')
        expect(submitButton).toHaveLength(1)
        expect(submitButton.props()).toStrictEqual({
          children: 'my-label',
          className: 'my-class',
          disabled: false,
          id: 'my-id',
          type: 'submit',
        })
      })
    })
  })
})
