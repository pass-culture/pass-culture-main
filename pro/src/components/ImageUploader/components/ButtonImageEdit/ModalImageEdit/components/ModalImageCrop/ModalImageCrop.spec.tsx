import * as Dialog from '@radix-ui/react-dialog'
import { userEvent } from '@testing-library/user-event'

import * as useAnalytics from 'app/App/analytics/firebase'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { UploaderModeEnum } from 'components/ImageUploader/types'

import { ModalImageCrop, ModalImageCropProps } from './ModalImageCrop'

const mockReplaceImage = vi.fn()
const mockDeleteImage = vi.fn()
const mockLogEvent = vi.fn()

const defaultProps: ModalImageCropProps = {
  image: new File([], 'toto.png', {
    type: 'image/png',
  }),
  onReplaceImage: mockReplaceImage,
  onImageDelete: mockDeleteImage,
  credit: 'Credits',
  onEditedImageSave: vi.fn(),
  saveInitialPosition: vi.fn(),
  onSetCredit: vi.fn(),
  mode: UploaderModeEnum.OFFER,
  initialScale: 1,
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

  it('log event on click', async () => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    const { getByText } = renderModalImageCrop()
    await userEvent.click(getByText('Suivant'))
    expect(mockLogEvent).toHaveBeenCalledOnce()
    expect(mockLogEvent).toHaveBeenNthCalledWith(1, 'hasClickedAddImage', {
      imageCreationStage: 'reframe image',
    })
  })

  it('should change credit when typing', async () => {
    const screen = renderModalImageCrop()
    const input = screen.getByRole('textbox')

    expect(input).toHaveValue('Credits')

    await userEvent.clear(input)

    await userEvent.type(input, 'New Credits')

    expect(input).toHaveValue('New Credits')
  })
})
