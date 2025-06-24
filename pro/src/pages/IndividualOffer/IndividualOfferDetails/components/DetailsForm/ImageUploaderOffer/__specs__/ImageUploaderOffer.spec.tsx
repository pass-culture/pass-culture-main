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

describe('ImageUploaderOffer', () => {
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
        name: /Illustrez votre offre/,
      })
    ).toBeInTheDocument()
    const infoBox = screen.getByText(
      'Ajoutez une image pour que votre offre ait 2 fois plus de chances d’être consultée !'
    )
    expect(infoBox).toBeInTheDocument()
    expect(imageUploaderOfferUtils.buildInitialValues).toHaveBeenCalledWith(
      undefined
    )
  })

  it('should render when an image is given', async () => {
    props.displayedImage = {
      url: 'https://test.url',
      credit: 'John Do',
    }
    renderImageUploaderOffer(props)

    expect(
      await screen.findByRole('heading', {
        name: /Illustrez votre offre/,
      })
    ).toBeInTheDocument()
    expect(imageUploaderOfferUtils.buildInitialValues).toHaveBeenCalledWith(
      props.displayedImage
    )
  })
})
