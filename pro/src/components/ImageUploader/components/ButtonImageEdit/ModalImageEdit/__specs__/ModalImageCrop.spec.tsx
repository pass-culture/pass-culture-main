import * as Dialog from '@radix-ui/react-dialog'
import { userEvent } from '@testing-library/user-event'

import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { UploaderModeEnum } from 'components/ImageUploader/types'

import {
  ModalImageCrop,
  ModalImageCropProps,
} from '../components/ModalImageCrop/ModalImageCrop'

const mockReplaceImage = vi.fn()
const mockDeleteImage = vi.fn()

const defaultProps: ModalImageCropProps = {
  image: new File([], 'toto.png', {
    type: 'image/png',
  }),
  onReplaceImage: mockReplaceImage,
  onImageDelete: mockDeleteImage,
  credit: '',
  onEditedImageSave: vi.fn(),
  saveInitialPosition: vi.fn(),
  onSetCredit: vi.fn(),
  mode: UploaderModeEnum.OFFER,
  showPreviewInModal: true,
}

function renderModalImageCrop() {
  return renderWithProviders(
    <Dialog.Root defaultOpen>
      <Dialog.Content aria-describedby={undefined}>
        <ModalImageCrop {...defaultProps} />
      </Dialog.Content>
    </Dialog.Root>
  )
}

describe('venue image edit', () => {
  it('calls the callback on remplacer button click', async () => {
    const { getByText } = renderModalImageCrop()
    await userEvent.click(getByText('Remplacer l’image'))
    expect(mockReplaceImage).toHaveBeenCalledTimes(1)
  })

  it('calls the callback on supprimer button click', async () => {
    const { getByText } = renderModalImageCrop()
    await userEvent.click(getByText('Supprimer l’image'))
    expect(mockDeleteImage).toHaveBeenCalledTimes(1)
  })
})
