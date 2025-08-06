import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { RootState } from '@/commons/store/rootReducer'

import { ButtonImageDelete, ButtonImageDeleteProps } from '../ButtonImageDelete'

interface RenderButtonImageDeleteProps {
  storeOverride?: Partial<RootState>
  props: ButtonImageDeleteProps
}
const renderButtonImageDelete = ({ props }: RenderButtonImageDeleteProps) => {
  render(<ButtonImageDelete {...props} />)
}

const mockOnDelete = vi.fn().mockResolvedValue({})

describe('ButtonImageDelete', () => {
  let props: ButtonImageDeleteProps

  beforeEach(() => {
    props = {
      onImageDelete: mockOnDelete,
    }
  })

  it('should render ButtonImageDelete', () => {
    renderButtonImageDelete({ props })

    expect(
      screen.getByRole('button', { name: /Supprimer/i })
    ).toBeInTheDocument()

    expect(screen.queryByText('Supprimer l’image')).not.toBeInTheDocument()
  })

  it('should open/close ModalImageDelete on click', async () => {
    renderButtonImageDelete({ props })

    await userEvent.click(screen.getByRole('button', { name: /Supprimer/i }))

    const modalPreview = await screen.findByText('Supprimer l’image')
    expect(modalPreview).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', { name: /Fermer la fenêtre modale/i })
    )

    expect(modalPreview).not.toBeInTheDocument()
  })
})
