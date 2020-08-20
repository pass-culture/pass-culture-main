import { mount } from 'enzyme'
import React from 'react'
import { MemoryRouter } from 'react-router'

import NotMatch from '../../../../pages/not-match/NotMatch'
import { ApiError } from '../../ApiError'
import AnyError from '../AnyError/AnyError'
import ErrorsPage from '../ErrorsPage'
import GatewayTimeoutError from '../GatewayTimeoutError/GatewayTimeoutError'
import { Children } from './Children'

describe('src | layout | PageErrors', () => {
  describe('when no http error', () => {
    it('should display the children', () => {
      // when
      const wrapper = mount(
        <ErrorsPage>
          <Children />
        </ErrorsPage>
      )

      // then
      const children = wrapper.find({ children: 'any child component' })
      expect(children).toHaveLength(1)
    })
  })

  describe('when 504 gateway timeout error', () => {
    it('should display an specific error message', () => {
      // given
      const error = new ApiError(504)

      // when
      const wrapper = mount(
        <ErrorsPage>
          <Children />
        </ErrorsPage>
      )
      wrapper.find(Children).simulateError(error)

      // then
      const gatewayTimeoutError = wrapper.find(GatewayTimeoutError)
      expect(gatewayTimeoutError).toHaveLength(1)
    })
  })

  describe('when 404 page not found error', () => {
    it('should display an specific error message', () => {
      // given
      const error = new ApiError(404)

      // when
      const wrapper = mount(
        <MemoryRouter>
          <ErrorsPage>
            <Children />
          </ErrorsPage>
        </MemoryRouter>
      )
      wrapper.find(Children).simulateError(error)

      // then
      const notMatch = wrapper.find(NotMatch)
      expect(notMatch).toHaveLength(1)
    })
  })

  describe('when other than 504 error', () => {
    it('should display an specific error message', () => {
      // given
      const error = new ApiError(500)

      // when
      const wrapper = mount(
        <ErrorsPage>
          <Children />
        </ErrorsPage>
      )
      wrapper.find(Children).simulateError(error)

      // then
      const anyError = wrapper.find(AnyError)
      expect(anyError).toHaveLength(1)
    })
  })
})
