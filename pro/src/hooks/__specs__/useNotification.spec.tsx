import '@testing-library/jest-dom'
import { render } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'

import useNotification from 'hooks/useNotification'
import * as notificationReducer from 'store/reducers/notificationReducer'
import { configureTestStore } from 'store/testUtils'

const TestComponent = (): JSX.Element | null => {
  const notify = useNotification()

  notify.success('notfication sucess', {
    duration: 1,
    withStickyActionBar: true,
  })
  notify.error('notfication error', {
    duration: 2,
  })
  notify.pending('notfication pending')
  notify.information('notfication information', {
    withStickyActionBar: true,
  })
  notify.close()

  return null
}

describe('useNotification', () => {
  it('should call functions for notifications with parameter', () => {
    jest.mock('store/reducers/notificationReducer', () => ({
      closeNotification: mockCloseNotification,
      showNotification: mockShowNotification,
    }))
    const mockCloseNotification = jest.spyOn(
      notificationReducer,
      'closeNotification'
    )
    const mockShowNotification = jest.spyOn(
      notificationReducer,
      'showNotification'
    )

    render(
      <Provider store={configureTestStore()}>
        <TestComponent />
      </Provider>
    )

    expect(mockShowNotification).toHaveBeenCalledTimes(4)
    expect(mockShowNotification).toHaveBeenNthCalledWith(1, {
      duration: 1,
      text: 'notfication sucess',
      type: 'success',
      withStickyActionBar: true,
    })
    expect(mockShowNotification).toHaveBeenNthCalledWith(2, {
      duration: 2,
      text: 'notfication error',
      type: 'error',
      withStickyActionBar: false,
    })
    expect(mockShowNotification).toHaveBeenNthCalledWith(3, {
      duration: 5000,
      text: 'notfication pending',
      type: 'pending',
      withStickyActionBar: false,
    })
    expect(mockShowNotification).toHaveBeenNthCalledWith(4, {
      duration: 5000,
      text: 'notfication information',
      type: 'information',
      withStickyActionBar: true,
    })
    expect(mockCloseNotification).toHaveBeenCalledTimes(1)
    expect(mockCloseNotification).toHaveBeenCalledWith()
  })
})
