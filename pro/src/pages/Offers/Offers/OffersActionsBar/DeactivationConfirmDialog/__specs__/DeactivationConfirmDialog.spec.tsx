import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { Audience } from 'core/shared/types'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  DeactivationConfirmDialog,
  DeactivationConfirmDialogProps,
} from '../DeactivationConfirmDialog'

const renderDeactivationConfirmDialog = ({
  ...props
}: DeactivationConfirmDialogProps) => {
  renderWithProviders(<DeactivationConfirmDialog {...props} />)
}

describe('DeactivationConfirmDialog', () => {
  const onCancelDialogMock = vi.fn()
  const onConfirmDialogMock = vi.fn()
  const props = {
    areAllOffersSelected: false,
    onCancel: onCancelDialogMock,
    nbSelectedOffers: 0,
    onConfirm: onConfirmDialogMock,
    audience: Audience.COLLECTIVE,
  }

  it('should called onCancel button onclick', async () => {
    renderDeactivationConfirmDialog({ ...props, nbSelectedOffers: 1 })

    const onCancelButton = screen.getByText('Annuler')
    await userEvent.click(onCancelButton)
    expect(onCancelDialogMock).toHaveBeenCalled()
  })

  it('should called onConfirm button onclick', async () => {
    renderDeactivationConfirmDialog({ ...props, nbSelectedOffers: 1 })

    const onConfirmButton = screen.getByText('Masquer')
    await userEvent.click(onConfirmButton)
    expect(onConfirmDialogMock).toHaveBeenCalled()
  })

  it('should render text for one offer', () => {
    renderDeactivationConfirmDialog({ ...props, nbSelectedOffers: 1 })

    expect(
      screen.getByText(/Vous avez sélectionné 1 offre/)
    ).toBeInTheDocument()
    expect(
      screen.getByText(/êtes-vous sûr de vouloir la masquer ?/)
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        /Dans ce cas, elle ne sera plus visible par les enseignants sur adage/
      )
    ).toBeInTheDocument()
  })

  it('should render text for multiple offers', () => {
    renderDeactivationConfirmDialog({ ...props, nbSelectedOffers: 2 })

    expect(
      screen.getByText(/Vous avez sélectionné 2 offres/)
    ).toBeInTheDocument()
    expect(
      screen.getByText(/êtes-vous sûr de vouloir toutes les masquer ?/)
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        /Dans ce cas, elles ne seront plus visibles par les enseignants sur adage./
      )
    ).toBeInTheDocument()
  })
})
