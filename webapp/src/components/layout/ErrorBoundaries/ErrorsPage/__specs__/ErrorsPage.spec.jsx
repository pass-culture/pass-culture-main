import { mount } from 'enzyme'
import React from 'react'

import AnyError from '../AnyError/AnyError'
import { ApiError } from '../ApiError'
import ErrorsPage from '../ErrorsPage'
import GatewayTimeoutError from '../GatewayTimeoutError/GatewayTimeoutError'
import ServiceUnavailable from '../ServiceUnavailable/ServiceUnavailable'
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
    it('should display a specific error message', () => {
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

  describe('when 503 service unavailable error', () => {
    it('should display a specific error message', () => {
      // given
      const error = new ApiError(503)

      // when
      const wrapper = mount(
        <ErrorsPage>
          <Children />
        </ErrorsPage>
      )
      wrapper.find(Children).simulateError(error)

      // then
      const serviceUnavailable = wrapper.find(ServiceUnavailable)
      expect(serviceUnavailable).toHaveLength(1)
    })
  })

  describe('when other than 504 error', () => {
    it('should display a specific error message', () => {
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

  describe('when other than http error', () => {
    it('should delegate to other error catcher', () => {
      // given
      const Children = () => {
        throw new Error('whatever')
      }

      // when
      const wrapper = () =>
        mount(
          <ErrorsPage>
            <Children />
          </ErrorsPage>
        )

      // then
      expect(wrapper).toThrow(Error)
    })
  })
})
