import * as snackBarReducer from '@/commons/store/snackBar/reducer'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { SnackBarVariant } from '@/design-system/SnackBar/SnackBar'

import { useSnackBar } from '../useSnackBar'

const TestComponent = (): JSX.Element | null => {
  const snackBar = useSnackBar()

  snackBar.success('notification success')
  snackBar.error('notification error')

  return null
}

describe('useSnackBar', () => {
  it('should call addSnackBar with correct parameters', () => {
    const mockAddSnackBar = vi.spyOn(snackBarReducer, 'addSnackBar')

    renderWithProviders(<TestComponent />)

    expect(mockAddSnackBar).toHaveBeenCalledTimes(2)
    expect(mockAddSnackBar).toHaveBeenNthCalledWith(1, {
      text: 'notification success',
      variant: SnackBarVariant.SUCCESS,
    })
    expect(mockAddSnackBar).toHaveBeenNthCalledWith(2, {
      text: 'notification error',
      variant: SnackBarVariant.ERROR,
    })
  })
})
