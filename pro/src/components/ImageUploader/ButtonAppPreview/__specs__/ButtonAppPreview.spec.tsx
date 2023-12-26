import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { UploaderModeEnum } from 'components/ImageUploader/types'
import { RootState } from 'store/rootReducer'

import ButtonAppPreview, { ButtonAppPreviewProps } from '../ButtonAppPreview'

interface RenderButtonAppPreviewProps {
  storeOverride?: Partial<RootState>
  props: ButtonAppPreviewProps
}
const renderButtonAppPreview = ({ props }: RenderButtonAppPreviewProps) => {
  return render(<ButtonAppPreview {...props} />)
}

describe('ButtonAppPreview', () => {
  let props: ButtonAppPreviewProps

  beforeEach(() => {
    props = {
      mode: UploaderModeEnum.OFFER,
      imageUrl: '/no-image.jpg',
    }
  })

  it('should render ButtonAppPreview', () => {
    renderButtonAppPreview({ props })

    expect(
      screen.getByRole('button', { name: /Prévisualiser/i })
    ).toBeInTheDocument()

    expect(
      screen.queryByRole('heading', { name: 'Image de l’offre' })
    ).not.toBeInTheDocument()
  })

  it('should open/close ModalAppPreview on click', async () => {
    renderButtonAppPreview({ props })

    await userEvent.click(
      screen.getByRole('button', { name: /Prévisualiser/i })
    )

    const modalPreview = await screen.findByRole('heading', {
      name: 'Ajouter une image',
    })
    expect(modalPreview).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', { name: /Fermer la modale/i })
    )

    expect(modalPreview).not.toBeInTheDocument()
  })
})
