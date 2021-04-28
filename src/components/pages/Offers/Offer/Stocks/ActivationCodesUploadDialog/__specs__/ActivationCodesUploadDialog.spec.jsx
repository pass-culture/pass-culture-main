import '@testing-library/jest-dom'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import React from 'react'

import ActivationCodesUploadDialog from '../ActivationCodesUploadDialog'

const renderActivationCodesUploadDialog = async props => {
  render(<ActivationCodesUploadDialog {...props} />)
}

describe('activation codes upload dialog', () => {
  const closeDialog = jest.fn()
  let props
  beforeEach(() => {
    props = { closeDialog }
  })
  afterEach(() => {
    closeDialog.mockClear()
  })

  it('render csv form when no file has been submitted', () => {
    // Given
    renderActivationCodesUploadDialog(props)

    // Then
    expect(
      screen.getByLabelText("Importer un fichier .csv depuis l'ordinateur")
    ).toBeInTheDocument()
  })

  it('should allow to upload csv file', async () => {
    // Given
    renderActivationCodesUploadDialog(props)
    const uploadButton = screen.getByLabelText("Importer un fichier .csv depuis l'ordinateur")
    const file = new File(["Vos codes d'activations\nABH\nJHB"], 'activation_codes.csv', {
      type: 'text/csv',
    })

    // When
    fireEvent.change(uploadButton, {
      target: {
        files: [file],
      },
    })

    // Then
    await waitFor(() =>
      expect(
        screen.getByText("Vous êtes sur le point d'ajouter 2 codes d'activation.")
      ).toBeInTheDocument()
    )
  })

  it('should not change step when file is null', async () => {
    // Given
    renderActivationCodesUploadDialog(props)
    const uploadButton = screen.getByLabelText("Importer un fichier .csv depuis l'ordinateur")

    // When
    fireEvent.change(uploadButton, {
      target: {
        files: [null],
      },
    })

    // Then
    await waitFor(() => {
      expect(
        screen.queryByText("Vous êtes sur le point d'ajouter 2 codes d'activations.")
      ).not.toBeInTheDocument()
      expect(
        screen.getByLabelText("Importer un fichier .csv depuis l'ordinateur")
      ).toBeInTheDocument()
    })
  })
})
