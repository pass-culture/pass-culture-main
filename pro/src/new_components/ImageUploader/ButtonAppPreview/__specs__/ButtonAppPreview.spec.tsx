import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { UploaderModeEnum } from 'new_components/ImageUploader/types'
import { RootState } from 'store/reducers'

import ButtonAppPreview, { IButtonAppPreviewProps } from '../ButtonAppPreview'

interface IRenderButtonAppPreviewProps {
  storeOverride?: Partial<RootState>
  props: IButtonAppPreviewProps
}
const renderButtonAppPreview = ({ props }: IRenderButtonAppPreviewProps) => {
  return render(<ButtonAppPreview {...props} />)
}

describe('ButtonAppPreview', () => {
  let props: IButtonAppPreviewProps

  beforeEach(() => {
    props = {
      mode: UploaderModeEnum.OFFER,
      imageUrl: '/no-image.jpg',
    }
  })

  it('should render ButtonAppPreview', async () => {
    await renderButtonAppPreview({
      props,
    })
    expect(
      screen.getByRole('button', { name: /Prévisualiser/i })
    ).toBeInTheDocument()

    expect(
      screen.queryByRole('heading', { name: "Image de l'offre" })
    ).not.toBeInTheDocument()
  })

  it('should open/close ModalAppPreview on click', async () => {
    await renderButtonAppPreview({
      props,
    })
    await userEvent.click(
      screen.getByRole('button', { name: /Prévisualiser/i })
    )

    const modalPreview = await screen.findByRole('heading', {
      name: "Image de l'offre",
    })
    expect(modalPreview).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', { name: /Fermer la modale/i })
    )

    expect(modalPreview).not.toBeInTheDocument()
  })
})
