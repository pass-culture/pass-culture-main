import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { Audience } from 'core/shared'
import { renderWithProviders } from 'utils/renderWithProviders'

import DeactivationConfirmDialog, {
  IDeactivationConfirmDialogProps,
} from '../DeactivationConfirmDialog'

const renderDeactivationConfirmDialog = ({
  ...props
}: IDeactivationConfirmDialogProps) => {
  renderWithProviders(<DeactivationConfirmDialog {...props} />)
}

describe('DeactivationConfirmDialog', () => {
  const onCancelDialogMock = jest.fn()
  const onConfirmDialogMock = jest.fn()
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

    const onConfirmButton = screen.getByText('Désactiver')
    await userEvent.click(onConfirmButton)
    expect(onConfirmDialogMock).toHaveBeenCalled()
  })

  it('should render text for one offer', async () => {
    renderDeactivationConfirmDialog({ ...props, nbSelectedOffers: 1 })

    expect(
      screen.getByText(/Vous avez sélectionné 1 offre/)
    ).toBeInTheDocument()
    expect(
      screen.getByText(/êtes-vous sûr de vouloir la désactiver ?/)
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        /Dans ce cas, elle ne sera plus visible par les enseignants sur adage/
      )
    ).toBeInTheDocument()
  })

  it('should render text for multiple offers', async () => {
    renderDeactivationConfirmDialog({ ...props, nbSelectedOffers: 2 })

    expect(
      screen.getByText(/Vous avez sélectionné 2 offres/)
    ).toBeInTheDocument()
    expect(
      screen.getByText(/êtes-vous sûr de vouloir toutes les désactiver ?/)
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        /Dans ce cas, elles ne seront plus visibles par les enseignants sur adage./
      )
    ).toBeInTheDocument()
  })
})
