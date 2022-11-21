import '@testing-library/jest-dom'

import { renderHook } from '@testing-library/react-hooks'
import React from 'react'
import { act } from 'react-dom/test-utils'
import { Provider } from 'react-redux'

import useNotification from 'hooks/useNotification'
import * as notificationReducer from 'store/reducers/notificationReducer'
import { configureTestStore } from 'store/testUtils'

describe('useNotification', () => {
  const wrapper = ({ children }: { children: any }) => (
    <Provider store={configureTestStore()}>{children}</Provider>
  )

  it('should display success notification', () => {
    const mockShowNotification = jest.spyOn(
      notificationReducer,
      'showNotification'
    )
    const { result } = renderHook(useNotification, {
      wrapper,
    })
    const notify = result.current

    act(() => {
      notify.success('notification sucess', {
        duration: 1,
      })
    })

    expect(mockShowNotification).toHaveBeenCalledTimes(1)
    expect(mockShowNotification).toHaveBeenNthCalledWith(1, {
      duration: 1,
      text: 'notification sucess',
      type: 'success',
    })
  })

  it('should display error notification', () => {
    const mockShowNotification = jest.spyOn(
      notificationReducer,
      'showNotification'
    )
    const { result } = renderHook(useNotification, {
      wrapper,
    })
    const notify = result.current

    act(() => {
      notify.error('notification error', {
        duration: 3,
      })
    })

    expect(mockShowNotification).toHaveBeenCalledTimes(1)
    expect(mockShowNotification).toHaveBeenNthCalledWith(1, {
      duration: 3,
      text: 'notification error',
      type: 'error',
    })
  })

  it('should display pending notification', () => {
    const mockShowNotification = jest.spyOn(
      notificationReducer,
      'showNotification'
    )
    const { result } = renderHook(useNotification, {
      wrapper,
    })
    const notify = result.current

    act(() => {
      notify.pending('notification pending', {
        duration: 2,
      })
    })

    expect(mockShowNotification).toHaveBeenCalledTimes(1)
    expect(mockShowNotification).toHaveBeenNthCalledWith(1, {
      duration: 2,
      text: 'notification pending',
      type: 'pending',
    })
  })

  it('should display information notification', () => {
    const mockShowNotification = jest.spyOn(
      notificationReducer,
      'showNotification'
    )
    const { result } = renderHook(useNotification, {
      wrapper,
    })
    const notify = result.current

    act(() => {
      notify.information('notification information', {
        duration: 5,
      })
    })

    expect(mockShowNotification).toHaveBeenCalledTimes(1)
    expect(mockShowNotification).toHaveBeenNthCalledWith(1, {
      duration: 5,
      text: 'notification information',
      type: 'information',
    })
  })

  it('should hide notification', () => {
    const mockCloseNotification = jest.spyOn(
      notificationReducer,
      'closeNotification'
    )
    const { result } = renderHook(useNotification, {
      wrapper,
    })
    const notify = result.current

    act(() => {
      notify.close()
    })

    expect(mockCloseNotification).toHaveBeenCalledTimes(1)
  })
})
