import { fireEvent, render, screen } from '@testing-library/react'

import { SafeImage } from './SafeImage'

function ImagePlaceholder() {
  return (
    <div>
      <p>Image corrompue, veuillez ajouter une nouvelle image</p>
    </div>
  )
}

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
  )
})
