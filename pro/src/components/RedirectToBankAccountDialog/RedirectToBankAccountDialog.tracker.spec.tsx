import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import * as useAnalytics from '@/app/App/analytics/firebase'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  RedirectToBankAccountDialog,
  type RedirectToBankAccountDialogProps,
} from './RedirectToBankAccountDialog'

const mockLogEvent = vi.fn()
const renderDialog = (props: RedirectToBankAccountDialogProps) => {
  renderWithProviders(<RedirectToBankAccountDialog {...props} />)
}

describe('screen Offers', () => {
  let props: RedirectToBankAccountDialogProps
  beforeEach(() => {
    props = {
      cancelRedirectUrl: '/url',
      offererId: 1,
      isDialogOpen: true,
    }

    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  it('should track event on cancel', async () => {
    renderDialog(props)

    await userEvent.click(screen.getByText('Plus tard'))

    expect(mockLogEvent).toHaveBeenCalledWith(
      'hasClickedSeeLaterFromSuccessOfferCreationModal'
    )
  })
  it('should track event on redirect', async () => {
    renderDialog(props)

    await userEvent.click(screen.getByText('Ajouter un compte bancaire'))

    expect(mockLogEvent).toHaveBeenCalledWith('hasClickedVenueAddRibButton')
  })
})
