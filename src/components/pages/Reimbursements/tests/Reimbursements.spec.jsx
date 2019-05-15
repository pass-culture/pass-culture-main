import React from 'react'
import { mount, shallow } from 'enzyme'

import Reimbursements from '../Reimbursements'

const mockRequestDataCatch = jest.fn()
jest.mock('redux-saga-data', () => {
  const actualModule = jest.requireActual('redux-saga-data')
  return {
    ...actualModule,
    requestData: config => {
      mockRequestDataCatch(config)
      return actualModule.requestData(config)
    },
  }
})

describe('src | components | pages | Reimbursements', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<Reimbursements />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
  describe('mount', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = mount(<Reimbursements />)

      console.log(wrapper.find('button[download]').props())
    })
  })
})
