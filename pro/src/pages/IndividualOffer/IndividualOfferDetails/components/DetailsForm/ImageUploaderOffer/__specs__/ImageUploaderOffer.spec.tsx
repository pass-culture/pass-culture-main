import { screen } from '@testing-library/react'

import { renderWithProviders } from 'commons/utils/renderWithProviders'

import * as imageUploaderOfferUtils from '../buildInitialValues'
import {
  ImageUploaderOffer,
  ImageUploaderOfferProps,
} from '../ImageUploaderOffer'

vi.mock('../buildInitialValues', () => ({
  buildInitialValues: vi.fn(),
}))

const renderImageUploaderOffer = (props: ImageUploaderOfferProps) =>
  renderWithProviders(<ImageUploaderOffer {...props} />)

describe('test ImageUploaderOffer', () => {
  let props: ImageUploaderOfferProps
  beforeEach(() => {
    props = {
      onImageUpload: vi.fn().mockResolvedValue(undefined),
      onImageDelete: vi.fn().mockResolvedValue(undefined),
    }
  })

  it('should render when no image is given', async () => {
    renderImageUploaderOffer(props)

    expect(
      await screen.findByRole('heading', {
        name: /Image de l’offre/,
      })
    ).toBeInTheDocument()
    const infoBox = screen.getByText(
      'Les offres avec une image ont 4 fois plus de chance d’être consultées que celles qui n’en ont pas.'
    )
    expect(infoBox).toBeInTheDocument()
    expect(imageUploaderOfferUtils.buildInitialValues).toHaveBeenCalledWith(
      undefined
    )
  })
  it('should render when an image is given', async () => {
    props.imageOffer = {
      originalUrl: 'https://test.url',
      url: 'https://test.url',
      credit: 'John Do',
    }
    renderImageUploaderOffer(props)

    expect(
      await screen.findByRole('heading', {
        name: /Image de l’offre/,
      })
    ).toBeInTheDocument()
    expect(imageUploaderOfferUtils.buildInitialValues).toHaveBeenCalledWith(
      props.imageOffer
    )
  })
})
