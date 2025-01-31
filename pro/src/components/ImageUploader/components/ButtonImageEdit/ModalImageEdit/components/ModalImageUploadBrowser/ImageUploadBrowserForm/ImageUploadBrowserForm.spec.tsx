import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import * as useAnalytics from 'app/App/analytics/firebase'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { createImageFile } from 'commons/utils/testFileHelpers'
import { UploaderModeEnum } from 'components/ImageUploader/types'

import { ImageUploadBrowserForm } from './ImageUploadBrowserForm'

const mockLogEvent = vi.fn()
const onSubmit = vi.fn()
const mockCreateImageBitmap = vi.fn()

Object.defineProperty(global, 'createImageBitmap', {
  writable: true,
  value: mockCreateImageBitmap,
})

const renderImageUploadBrowserForm = (
  mode: UploaderModeEnum = UploaderModeEnum.OFFER
) => {
  return renderWithProviders(
    <ImageUploadBrowserForm onSubmit={onSubmit} mode={mode} isReady />
  )
}

describe('ImageUploadBrowserForm', () => {
  it('render', () => {
    renderImageUploadBrowserForm()
    const fileInput = screen.getByLabelText(
      'Importer une image depuis l’ordinateur'
    )
    expect(fileInput).toBeInTheDocument()
  })

  it('should call onSubmit when file is valid', async () => {
    renderImageUploadBrowserForm()
    const fileInput = screen.getByLabelText(
      'Importer une image depuis l’ordinateur'
    )
    expect(fileInput).toBeInTheDocument()

    const testFile = createImageFile({
      name: 'hello.png',
      type: 'image/png',
      sizeInMB: 9,
      width: 400,
      height: 600,
    })

    await userEvent.upload(fileInput, testFile)
    expect(onSubmit).toHaveBeenCalledWith({ image: testFile })
  })

  it('should log an event on when using the button', async () => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    renderImageUploadBrowserForm()
    const fileInput = screen.getByLabelText(
      'Importer une image depuis l’ordinateur'
    )
    expect(fileInput).toBeInTheDocument()

    const testFile = createImageFile({
      name: 'hello.png',
      type: 'image/png',
      sizeInMB: 9,
      width: 400,
      height: 600,
    })

    await userEvent.upload(fileInput, testFile)
    expect(mockLogEvent).toHaveBeenCalledOnce()
    expect(mockLogEvent).toHaveBeenNthCalledWith(1, 'hasClickedAddImage', {
      imageCreationStage: 'import image',
    })
  })

  it('should display error when file is too big', async () => {
    renderImageUploadBrowserForm()
    const fileInput = screen.getByLabelText(
      'Importer une image depuis l’ordinateur'
    )

    const testFile = createImageFile({
      name: 'hello.png',
      type: 'image/png',
      sizeInMB: 11000000,
      width: 600,
    })

    await userEvent.upload(fileInput, testFile)
    expect(onSubmit).not.toHaveBeenCalled()
  })

  it("should display error when file's width is too small", async () => {
    renderImageUploadBrowserForm()
    const fileInput = screen.getByLabelText(
      'Importer une image depuis l’ordinateur'
    )

    const testFile = createImageFile({
      name: 'hello.png',
      type: 'image/png',
      sizeInMB: 9,
      width: 200,
    })

    await userEvent.upload(fileInput, testFile)
    expect(onSubmit).not.toHaveBeenCalled()
  })

  it("should display error when file's type is refused", async () => {
    renderImageUploadBrowserForm()
    const fileInput = screen.getByLabelText(
      'Importer une image depuis l’ordinateur'
    )

    const testFile = createImageFile({
      name: 'hello.png',
      type: 'image/png',
      sizeInMB: 9,
      width: 600,
    })

    await userEvent.upload(fileInput, testFile)
    expect(onSubmit).not.toHaveBeenCalled()
  })

  it("should display error when file's height and width is too small for portrait", async () => {
    renderImageUploadBrowserForm()
    const fileInput = screen.getByLabelText(
      'Importer une image depuis l’ordinateur'
    )

    const testFile = createImageFile({
      name: 'hello.png',
      type: 'image/png',
      sizeInMB: 9,
      width: 399,
      height: 400,
    })

    await userEvent.upload(fileInput, testFile)
    expect(onSubmit).not.toHaveBeenCalled()
    expect(
      screen.queryByText('Hauteur minimale de l’image : 600 px')
    ).toBeInTheDocument()
    expect(
      screen.queryByText('Largeur minimale de l’image : 400 px')
    ).toBeInTheDocument()
  })
})
