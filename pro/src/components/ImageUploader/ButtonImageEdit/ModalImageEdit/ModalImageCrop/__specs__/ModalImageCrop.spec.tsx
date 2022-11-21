import { render } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'

import { UploaderModeEnum } from 'components/ImageUploader/types'
import { configureTestStore } from 'store/testUtils'

import ModalImageCrop from '../ModalImageCrop'

const mockReplaceImage = jest.fn()
const defaultProps = {
  image: new File([], 'toto.png', {
    type: 'image/png',
  }),
  onSetImage: jest.fn(),
  onReplaceImage: mockReplaceImage,
  credit: '',
  onEditedImageSave: jest.fn(),
  saveInitialPosition: jest.fn(),
  saveInitialScale: jest.fn(),
  onSetCredit: jest.fn(),
  mode: UploaderModeEnum.OFFER,
  submitButtonText: 'Suivant',
}

describe('venue image edit', () => {
  it('closes the modal on cancel button click', async () => {
    const store = configureTestStore()
    const { getByText } = render(
      <Provider store={store}>
        <ModalImageCrop {...defaultProps} />
      </Provider>
    )
    await userEvent.click(getByText("Remplacer l'image"))
    expect(mockReplaceImage).toHaveBeenCalledTimes(1)
  })
})
