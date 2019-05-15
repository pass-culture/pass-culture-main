import React from 'react'
import { shallow } from 'enzyme'

import DownloadButton from '../DownloadButton'

describe('src | components | Layout | DownloadButton', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        downloadFileOrNotifyAnError: () => jest.fn(),
      }

      // when
      const wrapper = shallow(<DownloadButton {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
