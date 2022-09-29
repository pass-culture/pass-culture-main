import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'

import { configureTestStore } from 'store/testUtils'

import ImageUploaderOffer, {
  IImageUploaderOfferProps,
} from '../ImageUploaderOffer'
import * as imageUploaderOfferUtils from '../utils'

jest.mock('../utils', () => ({
  buildInitialValues: jest.fn(),
}))

const renderImageUploaderOffer = (props: IImageUploaderOfferProps) => {
  const store = configureTestStore()
  return render(
    <Provider store={store}>
      <ImageUploaderOffer {...props} />
    </Provider>
  )
}

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
        name: /Image de l'offre/,
      })
    ).toBeInTheDocument()
    const infoBox = screen.getByText(
      'Les offres avec une image ont 4 fois plus de chance d’être consultées que celles qui n’en ont pas.'
    )
    expect(infoBox).toBeInTheDocument()
    expect(imageUploaderOfferUtils.buildInitialValues).toHaveBeenCalledWith(
      undefined,
      undefined
    )
  })
  it('should render when an image is given', async () => {
    props.imageOffer = {
      url: 'http://test.url',
      credit: 'John Do',
    }
    renderImageUploaderOffer(props)

    expect(
      await screen.findByRole('heading', {
        name: /Image de l'offre/,
      })
    ).toBeInTheDocument()
    expect(imageUploaderOfferUtils.buildInitialValues).toHaveBeenCalledWith(
      ...Object.values(props.imageOffer)
    )
  })
})
