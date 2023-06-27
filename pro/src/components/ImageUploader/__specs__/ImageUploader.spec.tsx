import { screen } from '@testing-library/react'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import ImageUploader, { ImageUploaderProps } from '../ImageUploader'
import { UploaderModeEnum } from '../types'

const renderImageUploader = (props: ImageUploaderProps) =>
  renderWithProviders(<ImageUploader {...props} />)

describe('ImageUploader', () => {
  let props: ImageUploaderProps

  beforeEach(() => {
    props = {
      onImageUpload: async () => {},
      onImageDelete: async () => {},
      mode: UploaderModeEnum.OFFER,
      initialValues: {
        imageUrl: 'noimage.jpg',
        originalImageUrl: 'noimage.jpg',
        credit: 'John Do',
        cropParams: {
          xCropPercent: 100,
          yCropPercent: 100,
          heightCropPercent: 1,
          widthCropPercent: 1,
        },
      },
    }
  })

  it('should render image uploader for existing file', async () => {
    renderImageUploader(props)
    expect(
      screen.getByAltText('Prévisualisation de l’image')
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: /Modifier/i })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: /Prévisualiser/i })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: /Supprimer/i })
    ).toBeInTheDocument()

    expect(
      screen.queryByRole('button', { name: /Ajouter une image/i })
    ).not.toBeInTheDocument()
  })

  it('should render image uploader without file', async () => {
    props = {
      onImageUpload: async () => {},
      onImageDelete: async () => {},
      mode: UploaderModeEnum.OFFER,
    }
    renderImageUploader(props)
    expect(
      screen.queryByAltText('Prévisualisation de l’image')
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: /Modifier/i })
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: /Prévisualiser/i })
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: /Supprimer/i })
    ).not.toBeInTheDocument()

    expect(
      screen.getByRole('button', { name: /Ajouter une image/i })
    ).toBeInTheDocument()
  })
})
