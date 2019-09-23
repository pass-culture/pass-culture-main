import React from 'react'
import { shallow } from 'enzyme'

import FormFooter from '../FormFooter'

describe('src | components | forms | FormFooter', () => {
  describe('render', () => {
    const separatorSelector = 'hr.dotted-left-2x-white'

    it('hide separator when no submit and no cancel', () => {
      // given
      const props = {
        cancel: {
          disabled: false,
          label: '',
        },
        submit: {
          disabled: false,
          label: '',
        },
      }

      // when
      const wrapper = shallow(<FormFooter {...props} />)
      const separator = wrapper.find(separatorSelector)

      // then
      expect(separator).toHaveLength(0)
    })

    it('hide separator when no cancel', () => {
      // given
      const props = {
        submit: {
          disabled: false,
          id: 'fake submit id',
          label: 'fake submit label',
        },
      }

      // when
      const wrapper = shallow(<FormFooter {...props} />)
      const separator = wrapper.find(separatorSelector)

      // then
      expect(separator).toHaveLength(0)
    })

    it('hide separator when no submit', () => {
      // given
      const props = {
        cancel: {
          disabled: false,
          id: 'fake cancel id',
          label: 'fake cancel label',
          url: 'fake cancel url',
        },
      }

      // when
      const wrapper = shallow(<FormFooter {...props} />)
      const separator = wrapper.find(separatorSelector)

      // then
      expect(separator).toHaveLength(0)
    })

    it('show separator when cancel and submit with no url', () => {
      // given
      const props = {
        cancel: {
          disabled: false,
          id: 'fake cancel id',
          label: 'fake cancel label',
          url: 'fake cancel url',
        },
        submit: {
          disabled: false,
          id: 'fake submit id',
          label: 'fake submit label',
        },
      }

      // when
      const wrapper = shallow(<FormFooter {...props} />)
      const separator = wrapper.find(separatorSelector)

      // then
      expect(separator).toHaveLength(1)
    })

    it('show separator when cancel and submit with url', () => {
      // given
      const props = {
        cancel: {
          disabled: false,
          id: 'fake cancel id',
          label: 'fake cancel label',
          url: 'fake cancel url',
        },
        submit: {
          disabled: false,
          id: 'fake submit id',
          label: 'fake submit label',
          url: 'fake submit url',
        },
      }

      // when
      const wrapper = shallow(<FormFooter {...props} />)
      const separator = wrapper.find(separatorSelector)

      // then
      expect(separator).toHaveLength(1)
    })

    it('render submit as submit button', () => {
      // given
      const props = {
        submit: {
          disabled: false,
          id: 'fake submit id',
          label: 'fake submit label',
        },
      }

      // when
      const wrapper = shallow(<FormFooter {...props} />)
      const submitButtonProps = wrapper.find('button').props()

      // then
      expect(submitButtonProps.id).toStrictEqual('fake submit id')
    })

    it('render submit as text link', () => {
      // given
      const props = {
        submit: {
          disabled: false,
          id: 'fake submit id',
          label: 'fake submit label',
          url: 'fake submit url',
        },
      }

      // when
      const wrapper = shallow(<FormFooter {...props} />)
      const submitButtonProps = wrapper.find('Link').props()

      // then
      expect(submitButtonProps.id).toStrictEqual('fake submit id')
    })

    it('render cancel button only', () => {
      // given
      const props = {
        cancel: {
          disabled: false,
          id: 'fake cancel id',
          label: 'fake cancel label',
          url: 'fake cancel url',
        },
      }

      // when
      const wrapper = shallow(<FormFooter {...props} />)
      const submitButtonProps = wrapper.find('Link').props()

      // then
      expect(submitButtonProps.id).toStrictEqual('fake cancel id')
    })
  })

  describe('match the snapshots', () => {
    it('hidden separator, cancel and submit buttons', () => {
      // given
      const props = {
        cancel: {
          disabled: false,
          label: '',
        },
        className: 'fake className',
        submit: {
          disabled: false,
          label: '',
        },
      }

      // when
      const wrapper = shallow(<FormFooter {...props} />)

      // then
      expect(wrapper).toMatchSnapshot()
    })

    it('show submit as submit button', () => {
      // given
      const props = {
        cancel: {
          className: 'fake cancel className',
          disabled: false,
          id: 'fake cancel id',
          label: 'fake cancel label',
          url: 'fake cancel url',
        },
        className: 'fake className',
        submit: {
          className: 'fake submit className',
          disabled: false,
          id: 'fake submit id',
          label: 'fake submit label',
        },
      }

      // when
      const wrapper = shallow(<FormFooter {...props} />)

      // then
      expect(wrapper).toMatchSnapshot()
    })

    it('show submit as a text link', () => {
      // given
      const props = {
        cancel: {
          className: 'fake cancel className',
          disabled: false,
          id: 'fake cancel id',
          label: 'fake cancel label',
          url: 'fake cancel url',
        },
        className: 'fake className',
        submit: {
          className: 'fake submit className',
          disabled: false,
          id: 'fake submit id',
          label: 'fake submit label',
          url: 'fake submit url',
        },
      }

      // when
      const wrapper = shallow(<FormFooter {...props} />)

      // then
      expect(wrapper).toMatchSnapshot()
    })

    it('hide cancel button', () => {
      // given
      const props = {
        cancel: {
          disabled: false,
          label: '',
        },
        className: 'fake className',
        submit: {
          className: 'fake submit className',
          disabled: false,
          id: 'fake submit id',
          label: 'fake submit label',
          url: 'fake submit url',
        },
      }

      // when
      const wrapper = shallow(<FormFooter {...props} />)

      // then
      expect(wrapper).toMatchSnapshot()
    })
  })
})
