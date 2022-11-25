import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { UploaderModeEnum } from 'components/ImageUploader/types'

import ImageUploadBrowserForm from '../ImageUploadBrowserForm'

const onSubmit = jest.fn()

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
    Object.defineProperty(testFile, 'height', {
      value: 400,
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

  it("should display error when file's height is too small for portrait", async () => {
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
      value: 400,
      configurable: true,
    })
    Object.defineProperty(testFile, 'height', {
      value: 399,
      configurable: true,
    })

    await userEvent.upload(fileInput, testFile)
    expect(onSubmit).not.toHaveBeenCalled()
    expect(
      screen.queryByText('La hauteur minimale de l’image : 400 px')
    ).toBeInTheDocument()
  })

  it('should not display height message with venue mode', async () => {
    await renderImageUploadBrowserForm(UploaderModeEnum.VENUE)
    expect(
      screen.queryByText('La hauteur minimale de l’image : 400 px')
    ).not.toBeInTheDocument()
  })

  it('should display height message with offer mode', async () => {
    await renderImageUploadBrowserForm()
    expect(
      screen.queryByText('La hauteur minimale de l’image : 400 px')
    ).toBeInTheDocument()
  })

  it("should display error when file's ratio is too low in landscape", async () => {
    await renderImageUploadBrowserForm(UploaderModeEnum.VENUE)
    expect(
      screen.queryByText("La hauteur de l'image n'est pas assez grande.")
    ).not.toBeInTheDocument()
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
      value: 600,
      configurable: true,
    })
    Object.defineProperty(testFile, 'height', {
      value: 2,
      configurable: true,
    })

    await userEvent.upload(fileInput, testFile)
    expect(onSubmit).not.toHaveBeenCalled()
    expect(
      screen.queryByText("La hauteur de l'image n'est pas assez grande.")
    ).toBeInTheDocument()
  })
})
