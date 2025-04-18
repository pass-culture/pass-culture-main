import { useNotification } from 'commons/hooks/useNotification'
import * as notificationReducer from 'commons/store/notifications/reducer'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

const TestComponent = (): JSX.Element | null => {
  const notify = useNotification()

  notify.success('notfication sucess', {
    duration: 1,
  })
  notify.error('notfication error', {
    duration: 2,
  })
  notify.information('notfication information')
  notify.close()

  return null
}

describe('useNotification', () => {
  it('should call functions for notifications with parameter', () => {
    const mockCloseNotification = vi.spyOn(
      notificationReducer,
      'closeNotification'
    )
    const mockShowNotification = vi.spyOn(
      notificationReducer,
      'showNotification'
    )

    renderWithProviders(<TestComponent />)

    expect(mockShowNotification).toHaveBeenCalledTimes(3)
    expect(mockShowNotification).toHaveBeenNthCalledWith(1, {
      duration: 1,
      text: 'notfication sucess',
      type: 'success',
    })
    expect(mockShowNotification).toHaveBeenNthCalledWith(2, {
      duration: 2,
      text: 'notfication error',
      type: 'error',
    })
    expect(mockShowNotification).toHaveBeenNthCalledWith(3, {
      duration: 5000,
      text: 'notfication information',
      type: 'information',
    })
    expect(mockCloseNotification).toHaveBeenCalledTimes(1)
    expect(mockCloseNotification).toHaveBeenCalledWith()
  })
})
