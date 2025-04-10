import * as Dialog from '@radix-ui/react-dialog'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import * as useAnalytics from 'app/App/analytics/firebase'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { UploaderModeEnum } from 'components/ImageUploader/types'

import { ModalImageCrop, ModalImageCropProps } from './ModalImageCrop'

const credit = 'John Doe'
const onReplaceImage = vi.fn()
const onImageDelete = vi.fn()

const defaultProps: ModalImageCropProps = {
  image: new File(['dummy content'], 'test.png', { type: 'image/png' }),
  onReplaceImage: onReplaceImage,
  onImageDelete: onImageDelete,
  initialCredit: credit,
  onEditedImageSave: vi.fn(),
  saveInitialPosition: vi.fn(),
  mode: UploaderModeEnum.OFFER,
}

const mockLogEvent = vi.fn()

const renderModalImageCrop = () => {
  return renderWithProviders(
    <Dialog.Root defaultOpen>
      <Dialog.Content aria-describedby={undefined}>
        <ModalImageCrop {...defaultProps} />
      </Dialog.Content>
    </Dialog.Root>
  )
}

describe('ModalImageCrop', () => {
  it('handles credit input change', async () => {
    const { getByLabelText } = renderModalImageCrop()

    const input = getByLabelText('Crédit de l’image')
    await userEvent.clear(input)

    await userEvent.type(input, 'Jane Smith')

    expect(input).toHaveValue('Jane Smith')
  })

  it('calls onReplaceImage when replace button is clicked', async () => {
    renderModalImageCrop()

    await userEvent.click(screen.getByText('Remplacer l’image'))
    expect(onReplaceImage).toHaveBeenCalled()
  })

  it('calls onImageDelete when delete button is clicked', async () => {
    renderModalImageCrop()

    await userEvent.click(screen.getByText('Supprimer l’image'))
    expect(onImageDelete).toHaveBeenCalled()
  })

  it('log event on click', async () => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    const { getByText } = renderModalImageCrop()

    await userEvent.click(getByText('Enregistrer'))

    expect(mockLogEvent).toHaveBeenCalledOnce()

    expect(mockLogEvent).toHaveBeenNthCalledWith(1, 'hasClickedAddImage', {
      imageCreationStage: 'reframe image',
    })
  })
})
