import { screen } from '@testing-library/react'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import ImageUploaderOffer, {
  IImageUploaderOfferProps,
} from '../ImageUploaderOffer'
import * as imageUploaderOfferUtils from '../utils'

jest.mock('../utils', () => ({
  buildInitialValues: jest.fn(),
}))

const renderImageUploaderOffer = (props: IImageUploaderOfferProps) =>
  renderWithProviders(<ImageUploaderOffer {...props} />)

describe('test ImageUploaderOffer', () => {
  let props: IImageUploaderOfferProps
  beforeEach(() => {
    props = {
      onImageUpload: jest.fn().mockResolvedValue(undefined),
      onImageDelete: jest.fn().mockResolvedValue(undefined),
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
