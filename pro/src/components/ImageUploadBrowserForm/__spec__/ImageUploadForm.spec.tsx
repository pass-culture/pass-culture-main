import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { UploaderModeEnum } from 'components/ImageUploader/types'
import { createImageFile } from 'utils/testFileHelpers'

import ImageUploadBrowserForm from '../ImageUploadBrowserForm'

const onSubmit = vi.fn()
const mockCreateImageBitmap = vi.fn()

Object.defineProperty(global, 'createImageBitmap', {
  writable: true,
  value: mockCreateImageBitmap,
})

const renderImageUploadBrowserForm = (
  mode: UploaderModeEnum = UploaderModeEnum.OFFER
) => {
  return render(<ImageUploadBrowserForm onSubmit={onSubmit} mode={mode} />)
}

describe('ImageUploadBrowserForm', () => {
  it('render', async () => {
    await renderImageUploadBrowserForm()
    const fileInput = screen.getByLabelText(
      'Importer une image depuis l’ordinateur'
    )
    expect(fileInput).toBeInTheDocument()
  })

  it('should call onSubmit when file is valid', async () => {
    await renderImageUploadBrowserForm()
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

  it('should display error when file is too big', async () => {
    await renderImageUploadBrowserForm()
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
    await renderImageUploadBrowserForm()
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
    await renderImageUploadBrowserForm()
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
    await renderImageUploadBrowserForm()
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
