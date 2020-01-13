import React from 'react'
import { shallow } from 'enzyme'

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
          externalLink: null,
          submit: {
            className: 'my-class',
            disabled: false,
            id: 'my-id',
            label: 'my-label',
            url: 'my-url',
          },
        }

        // when
        const wrapper = shallow(<FormFooter {...props} />)

        // then
        const regularLink = wrapper.find(Link)
        expect(regularLink).toHaveLength(1)
        expect(regularLink.props()).toStrictEqual({
          children: 'my-label',
          className: 'flex-1 my-class',
          disabled: false,
          id: 'my-id',
          to: 'my-url'
        })
      })

      it('should render a cancel link when a cancel url is provided', () => {
        // given
        const props = {
          cancel: {
            className: 'my-class',
            disabled: false,
            id: 'my-id',
            label: 'my-label',
            url: 'my-url',
          },
          className: null,
          externalLink: null,
          submit: null,
        }

        // when
        const wrapper = shallow(<FormFooter {...props} />)

        // then
        const cancelLink = wrapper.find(Link)
        expect(cancelLink).toHaveLength(1)
        expect(cancelLink.props()).toStrictEqual({
          children: 'my-label',
          className: 'flex-1 my-class',
          disabled: false,
          id: 'my-id',
          to: 'my-url'
        })
      })
    })

    describe('external links', () => {
      it('should render an external link when an url is provided', () => {
        // given
        const props = {
          cancel: null,
          className: null,
          externalLink: {
            className: 'my-class',
            id: 'my-id',
            label: 'my-label',
            title: 'my-title',
            url: 'my-url',
          },
          submit: null
        }

        // when
        const wrapper = shallow(<FormFooter {...props} />)

        // then
        const externalLink = wrapper.find('a')
        expect(externalLink).toHaveLength(1)
        expect(externalLink.props()).toStrictEqual({
          children: 'my-label',
          className: 'flex-1 my-class',
          href: 'my-url',
          id: 'my-id',
          'onClick': expect.any(Function),
          'onKeyPress': expect.any(Function),
          role: 'button',
          tabIndex: '0',
          target: '_blank',
          title: 'my-title'
        })
      })
    })

    describe('buttons', () => {
      it('should render a submit button when an url is not provided', () => {
        // given
        const props = {
          cancel: null,
          className: null,
          externalLink: null,
          submit: {
            className: 'my-class',
            disabled: false,
            id: 'my-id',
            label: 'my-label',
          },
        }

        // when
        const wrapper = shallow(<FormFooter {...props} />)

        // then
        const submitButton = wrapper.find('button')
        expect(submitButton).toHaveLength(1)
        expect(submitButton.props()).toStrictEqual({
          children: 'my-label',
          className: 'flex-1 my-class',
          disabled: false,
          id: 'my-id',
          type: 'submit'
        })
      })
    })
  })
})
