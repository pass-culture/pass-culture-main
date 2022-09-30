import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import ActivationCodesUploadDialog from 'components/pages/Offers/Offer/Stocks/ActivationCodesUploadDialog/ActivationCodesUploadDialog'
import { configureTestStore } from 'store/testUtils'

const renderActivationCodesUploadDialog = (store, props = {}) => {
  render(<ActivationCodesUploadDialog {...props} />)
}

describe('activationCodesUploadDialog', () => {
  describe('uI Tests', () => {
    let store

    beforeEach(() => {
      store = configureTestStore({
        user: {
          currentUser: {
            id: 'test_id',
            hasSeenProTutorials: true,
          },
        },
      })
    })

    it('should display an error when the file violates activation codes upload checks', async () => {
      // Given
      const props = {
        activationCodes: [],
        changeActivationCodesExpirationDatetime: jest.fn(),
        closeDialog: jest.fn(),
        setActivationCodes: jest.fn(),
        today: new Date(),
        validateActivationCodes: jest.fn(),
      }

      // When
      renderActivationCodesUploadDialog(store, props)

      const uploadButton = screen.getByLabelText(
        'Importer un fichier .csv depuis l’ordinateur'
      )
      const file = new File(
        ['ABH\nJHB\nJHB\nCEG\nCEG'],
        'activation_codes.csv',
        {
          type: 'text/csv',
        }
      )

      expect(
        screen.getByTestId('activation-codes-upload-icon-id')
      ).toBeInTheDocument()

      await userEvent.upload(uploadButton, file)

      // Then
      expect(
        screen.getByText(
          'Une erreur s’est produite lors de l’import de votre fichier',
          { exact: false }
        )
      ).toBeInTheDocument()

      expect(
        screen.getByText(
          'Plusieurs codes identiques ont été trouvés dans le fichier : JHB, CEG.'
        )
      ).toBeInTheDocument()

      expect(
        screen.getByTestId('activation-codes-upload-error-icon-id')
      ).toBeInTheDocument()
    })
  })
})
