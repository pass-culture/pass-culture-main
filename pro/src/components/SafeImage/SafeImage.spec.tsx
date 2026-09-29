import { fireEvent, render, screen } from '@testing-library/react'

import { ImagePlaceholder } from './ImagePlaceholder/ImagePlaceholder'
import { SafeImage } from './SafeImage'

it('should render image', () => {
  render(
    <SafeImage
      src="my-url"
      alt=""
      testId="image"
      placeholder={<ImagePlaceholder />}
    />
  )

  expect(screen.getByTestId('image')).toBeInTheDocument()
  expect(document.querySelector('figure')).not.toBeInTheDocument()
  expect(screen.getByTestId('image')).not.toHaveAttribute('aria-describedby')
})

it('should render a figure and caption when a credit is provided', () => {
  render(
    <SafeImage
      src="my-url"
      alt="Un paysage"
      credit="Photographe"
      testId="image"
      placeholder={<ImagePlaceholder />}
    />
  )

  const caption = screen
    .getByText('Crédit image : Photographe')
    .closest('figcaption')
  expect(caption).toBeInTheDocument()
  expect(caption?.parentElement).toBe(screen.getByTestId('image').parentElement)
  expect(screen.getByTestId('image')).toHaveAttribute(
    'aria-describedby',
    caption?.id
  )
})

it('should render placeholder when image is broken', () => {
  render(
    <SafeImage
      src=""
      alt=""
      testId="image"
      placeholder={<ImagePlaceholder />}
    />
  )

  const image = screen.getByTestId('image')

  fireEvent.error(image)

  expect(screen.queryByTestId('image')).not.toBeInTheDocument()
  expect(
    screen.getByText('Image corrompue, veuillez ajouter une nouvelle image')
  ).toBeInTheDocument()
})
