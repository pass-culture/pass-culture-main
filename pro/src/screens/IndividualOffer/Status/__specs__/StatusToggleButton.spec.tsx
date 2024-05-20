import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { OfferStatus } from 'apiClient/v1'
import * as useNotification from 'hooks/useNotification'
import { renderWithProviders } from 'utils/renderWithProviders'

import StatusToggleButton, {
  StatusToggleButtonProps,
} from '../StatusToggleButton'

const renderStatusToggleButton = (props: StatusToggleButtonProps) =>
  renderWithProviders(<StatusToggleButton {...props} />)

describe('StatusToggleButton', () => {
  let props: StatusToggleButtonProps
  const offerId = 12
  beforeEach(() => {
    props = {
      offerId: offerId,
      isActive: true,
      status: OfferStatus.ACTIVE,
    }
  })

  it('should deactivate an offer and confirm', async () => {
    // given
    const toggle = vi.spyOn(api, 'patchOffersActiveStatus').mockResolvedValue()
    const notifySuccess = vi.fn()
    vi.spyOn(useNotification, 'default').mockImplementation(() => ({
      success: notifySuccess,
      error: vi.fn(),
      information: vi.fn(),
      pending: vi.fn(),
      close: vi.fn(),
    }))

    // when
    renderStatusToggleButton(props)

    // then
    await userEvent.click(screen.getByRole('button', { name: /Désactiver/ }))

    expect(toggle).toHaveBeenCalledTimes(1)
    expect(toggle).toHaveBeenNthCalledWith(1, {
      ids: [offerId],
      isActive: false,
    })
    expect(notifySuccess).toHaveBeenNthCalledWith(
      1,
      'L’offre a bien été désactivée.'
    )
  })

  it('should activate an offer and confirm', async () => {
    // given
    const toggleFunction = vi
      .spyOn(api, 'patchOffersActiveStatus')
      .mockResolvedValue()
    const notifySuccess = vi.fn()
    vi.spyOn(useNotification, 'default').mockImplementation(() => ({
      success: notifySuccess,
      error: vi.fn(),
      information: vi.fn(),
      pending: vi.fn(),
      close: vi.fn(),
    }))

    // when
    renderStatusToggleButton({
      ...props,
      isActive: false,
      status: OfferStatus.INACTIVE,
    })

    // then
    await userEvent.click(screen.getByText(/Publier/))
    expect(toggleFunction).toHaveBeenCalledTimes(1)
    expect(toggleFunction).toHaveBeenNthCalledWith(1, {
      ids: [offerId],
      isActive: true,
    })
    expect(notifySuccess).toHaveBeenNthCalledWith(
      1,
      'L’offre a bien été publiée.'
    )
  })

  it('should display error', async () => {
    // given
    const toggleFunction = vi
      .spyOn(api, 'patchOffersActiveStatus')
      .mockRejectedValue({})
    const notifyError = vi.fn()
    vi.spyOn(useNotification, 'default').mockImplementation(() => ({
      error: notifyError,
      success: vi.fn(),
      information: vi.fn(),
      pending: vi.fn(),
      close: vi.fn(),
    }))

    // when
    renderStatusToggleButton(props)

    // then
    await userEvent.click(screen.getByText(/Désactiver/))
    expect(toggleFunction).toHaveBeenCalledTimes(1)
    expect(notifyError).toHaveBeenNthCalledWith(
      1,
      'Une erreur est survenue, veuillez réessayer ultérieurement.'
    )
  })
})
