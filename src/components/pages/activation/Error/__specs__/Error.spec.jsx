import { shallow } from 'enzyme'
import React from 'react'

import { SUPPORT_EMAIL, SUPPORT_EMAIL_SUBJECT } from '../../../../../utils/config'
import MailToLink from '../../../../layout/MailToLink/MailToLink'
import Error from '../Error'

describe('src | components | pages | activation | Error', () => {
  it('should pass props to MailToLink component', () => {
    // when
    const wrapper = shallow(<Error />)
    const mailToLink = wrapper.find(MailToLink)

    // then
    expect(mailToLink).toHaveLength(1)
    expect(mailToLink.prop('email')).toStrictEqual(SUPPORT_EMAIL)
    expect(mailToLink.prop('headers')).toStrictEqual({
      subject: decodeURI(SUPPORT_EMAIL_SUBJECT),
    })
  })
})
