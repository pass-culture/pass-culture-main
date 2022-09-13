import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { UploaderModeEnum } from 'new_components/ImageUploader/types'

import ImageUploadBrowserForm from '../ImageUploadBrowserForm'

const onSubmit = jest.fn()

const renderImageUploadBrowserForm = () => {
  return render(
    <ImageUploadBrowserForm onSubmit={onSubmit} mode={UploaderModeEnum.OFFER} />
  )
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

    const testFile = new File([''], 'hello.png', {
      type: 'image/png',
    })
    Object.defineProperty(testFile, 'size', {
      value: 9000000,
      configurable: true,
    })
    Object.defineProperty(testFile, 'width', {
      value: 600,
      configurable: true,
    })

    await userEvent.upload(fileInput, testFile)
    expect(onSubmit).toHaveBeenCalledWith({ image: testFile })
  })

  it('should display error when file is too big', async () => {
    await renderImageUploadBrowserForm()
    const fileInput = screen.getByLabelText(
      'Importer une image depuis l’ordinateur'
    )

    const testFile = new File([''], 'hello.png', {
      type: 'image/png',
    })
    Object.defineProperty(testFile, 'size', {
      value: 11000000,
      configurable: true,
    })
    Object.defineProperty(testFile, 'width', {
      value: 600,
      configurable: true,
    })

    await userEvent.upload(fileInput, testFile)
    expect(onSubmit).not.toHaveBeenCalled()
  })

  it("should display error when file's width is too small", async () => {
    await renderImageUploadBrowserForm()
    const fileInput = screen.getByLabelText(
      'Importer une image depuis l’ordinateur'
    )

    const testFile = new File([''], 'hello.png', {
      type: 'image/png',
    })
    Object.defineProperty(testFile, 'size', {
      value: 9000000,
      configurable: true,
    })
    Object.defineProperty(testFile, 'width', {
      value: 200,
      configurable: true,
    })

    await userEvent.upload(fileInput, testFile)
    expect(onSubmit).not.toHaveBeenCalled()
  })

  it("should display error when file's type is refused", async () => {
    await renderImageUploadBrowserForm()
    const fileInput = screen.getByLabelText(
      'Importer une image depuis l’ordinateur'
    )

    const testFile = new File([''], 'hello.png', {
      type: 'image/gif',
    })
    Object.defineProperty(testFile, 'size', {
      value: 9000000,
      configurable: true,
    })
    Object.defineProperty(testFile, 'width', {
      value: 600,
      configurable: true,
    })

    await userEvent.upload(fileInput, testFile)
    expect(onSubmit).not.toHaveBeenCalled()
  })
})
