import * as Dialog from '@radix-ui/react-dialog'
import { userEvent } from '@testing-library/user-event'

import * as useAnalytics from 'app/App/analytics/firebase'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { UploaderModeEnum } from 'components/ImageUploader/types'

import {
  ModalImageUploadConfirm,
  ModalImageUploadConfirmProps,
} from './ModalImageUploadConfirm'

const mockLogEvent = vi.fn()

const defaultProps: ModalImageUploadConfirmProps = {
  imageUrl: 'imageUrl',
  mode: UploaderModeEnum.OFFER,
  isUploading: false,
  onGoBack: () => {},
  onUploadImage: () => {},
}

function renderModalImageUploadConfirm() {
  return renderWithProviders(
    <Dialog.Root defaultOpen>
      <Dialog.Content aria-describedby={undefined}>
        <ModalImageUploadConfirm {...defaultProps} />
      </Dialog.Content>
    </Dialog.Root>
  )
}

describe('ModalImageUploadConfirm', () => {
  beforeEach(() => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  it('log event on submit', async () => {
    const { getByText } = renderModalImageUploadConfirm()
    await userEvent.click(getByText('Enregistrer'))
    expect(mockLogEvent).toHaveBeenCalledOnce()
    expect(mockLogEvent).toHaveBeenNthCalledWith(1, 'hasClickedAddImage', {
      imageCreationStage: 'save image',
    })
  })
})
