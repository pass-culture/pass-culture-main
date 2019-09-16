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
    })
  })
})
