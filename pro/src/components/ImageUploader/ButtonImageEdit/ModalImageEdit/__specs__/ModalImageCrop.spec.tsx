import { userEvent } from '@testing-library/user-event'

import { UploaderModeEnum } from 'components/ImageUploader/types'
import { renderWithProviders } from 'utils/renderWithProviders'

import { ModalImageCrop } from '../ModalImageCrop'

const mockReplaceImage = vi.fn()
const mockDeleteImage = vi.fn()

const defaultProps = {
  image: new File([], 'toto.png', {
    type: 'image/png',
  }),
  onSetImage: vi.fn(),
  onReplaceImage: mockReplaceImage,
  onImageDelete: mockDeleteImage,
  credit: '',
  onEditedImageSave: vi.fn(),
  saveInitialPosition: vi.fn(),
  saveInitialScale: vi.fn(),
  onSetCredit: vi.fn(),
  mode: UploaderModeEnum.OFFER,
  submitButtonText: 'Suivant',
  idLabelledBy: 'some id',
}

describe('venue image edit', () => {
  it('calls the callback on remplacer button click', async () => {
    const { getByText } = renderWithProviders(
      <ModalImageCrop {...defaultProps} />
    )
    await userEvent.click(getByText('Remplacer l’image'))
    expect(mockReplaceImage).toHaveBeenCalledTimes(1)
  })

  it('calls the callback on supprimer button click', async () => {
    const { getByText } = renderWithProviders(
      <ModalImageCrop {...defaultProps} />
    )
    await userEvent.click(getByText('Supprimer l’image'))
    expect(mockDeleteImage).toHaveBeenCalledTimes(1)
  })
})
