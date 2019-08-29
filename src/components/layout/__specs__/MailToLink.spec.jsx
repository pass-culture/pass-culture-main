import React from 'react'
import { shallow } from 'enzyme'

import MailToLink from '../MailToLink'

const children = (
  <header>
    <h1>{'Fake children'}</h1>
  </header>
)

describe('src | components | share | MailToLink', () => {
  it('should match the snapshot', () => {
    // given
    const props = {
      children,
      email: 'email@fake.com',
      header: {},
    }

    // when
    const wrapper = shallow(<MailToLink {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('onClickShare', () => {
    describe('when obfuscate is false', () => {
      it('should render Link', () => {
        // given
        const props = {
          children,
          email: 'email@fake.com',
          header: {},
        }

        // when
        const wrapper = shallow(<MailToLink {...props} />)

        // // then
        expect(wrapper.find('a').props().href).toStrictEqual('mailto:email@fake.com?')
      })
    })

    describe('when obfuscate is true', () => {
      // given
      const props = {
        children,
        email: 'email@fake.com',
        headers: {
          body: 'http://localhost:3000/decouverte/AE/?shared_by=AE',
          subject: 'Fake Title',
        },
        obfuscate: true,
      }

      it('should render Obfuscated Link ', () => {
        // when
        const wrapper = shallow(<MailToLink {...props} />)

        // then
        expect(wrapper.find('a').props().href).toStrictEqual('mailto:obfuscated')
      })

      it.skip('should change window location on click', () => {
        // FIXME
        // Need to mock window.location.href
        // when
        const wrapper = shallow(<MailToLink {...props} />)
        const event = Object.assign(jest.fn(), { preventDefault: () => {} })
        wrapper.find('a').simulate('click', event)

        // then
        expect(window.location.href).toStrictEqual(
          'mailto:email@fake.com?body=http%3A%2F%2Flocalhost%3A3000%2Fdecouverte%2FAE%2F%3Fshared_by%3DAE&subject=Fake%20Title'
        )
      })
    })
  })
})
