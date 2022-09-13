import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { RootState } from 'store/reducers'
import StoreProvider from 'store/StoreProvider/StoreProvider'

import ButtonImageDelete, {
  IButtonImageDeleteProps,
} from '../ButtonImageDelete'

interface IRenderButtonImageDeleteProps {
  storeOverride?: Partial<RootState>
  props: IButtonImageDeleteProps
}
const renderButtonImageDelete = ({ props }: IRenderButtonImageDeleteProps) => {
  return render(
    <StoreProvider isDev>
      <ButtonImageDelete {...props} />
    </StoreProvider>
  )
}

const mockOnDelete = jest.fn().mockResolvedValue({})

describe('ButtonImageDelete', () => {
  let props: IButtonImageDeleteProps

  beforeEach(() => {
    props = {
      onImageDelete: mockOnDelete,
    }
  })

  it('should render ButtonImageDelete', async () => {
    await renderButtonImageDelete({
      props,
    })
    expect(
      screen.getByRole('button', { name: /Supprimer/i })
    ).toBeInTheDocument()

    expect(screen.queryByText("Supprimer l'image")).not.toBeInTheDocument()
  })

  it('should open/close ModalImageDelete on click', async () => {
    await renderButtonImageDelete({
      props,
    })
    await userEvent.click(screen.getByRole('button', { name: /Supprimer/i }))

    const modalPreview = await screen.findByText("Supprimer l'image")
    expect(modalPreview).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', { name: /Fermer la modale/i })
    )

    expect(modalPreview).not.toBeInTheDocument()
  })
})
