import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { RootState } from 'store/reducers'
import StoreProvider from 'store/StoreProvider/StoreProvider'

import ButtonImageDelete, { ButtonImageDeleteProps } from '../ButtonImageDelete'

interface RenderButtonImageDeleteProps {
  storeOverride?: Partial<RootState>
  props: ButtonImageDeleteProps
}
const renderButtonImageDelete = ({ props }: RenderButtonImageDeleteProps) => {
  render(
    <StoreProvider>
      <ButtonImageDelete {...props} />
    </StoreProvider>
  )
}

const mockOnDelete = vi.fn().mockResolvedValue({})

describe('ButtonImageDelete', () => {
  let props: ButtonImageDeleteProps

  beforeEach(() => {
    props = {
      onImageDelete: mockOnDelete,
    }
  })

  it('should render ButtonImageDelete', async () => {
    renderButtonImageDelete({
      props,
    })
    expect(
      await screen.findByRole('button', { name: /Supprimer/i })
    ).toBeInTheDocument()

    expect(screen.queryByText('Supprimer l’image')).not.toBeInTheDocument()
  })

  it('should open/close ModalImageDelete on click', async () => {
    renderButtonImageDelete({
      props,
    })
    await userEvent.click(
      await screen.findByRole('button', { name: /Supprimer/i })
    )

    const modalPreview = await screen.findByText('Supprimer l’image')
    expect(modalPreview).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', { name: /Fermer la modale/i })
    )

    expect(modalPreview).not.toBeInTheDocument()
  })
})
