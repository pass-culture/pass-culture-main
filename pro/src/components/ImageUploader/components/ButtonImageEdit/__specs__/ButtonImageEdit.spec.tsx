import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { UploaderModeEnum } from '@/commons/utils/imageUploadTypes'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { ButtonImageEdit, type ButtonImageEditProps } from '../ButtonImageEdit'

const snackBarSuccess = vi.fn()
const snackBarError = vi.fn()

vi.mock('@/commons/hooks/useSnackBar', () => ({
  useSnackBar: () => ({
    success: snackBarSuccess,
    error: snackBarError,
  }),
}))

vi.mock('@/components/ModalImageUpsertOrEdit/ModalImageUpsertOrEdit', () => ({
  ModalImageUpsertOrEdit: ({
    trigger,
    onImageDelete,
    onImageUpload,
  }: {
    trigger: React.ReactNode
    onImageDelete: () => void
    onImageUpload: (values: unknown, successMessage: string) => void
  }) => (
    <div>
      {trigger}
      <button
        type="button"
        aria-label="Supprimer l’image"
        onClick={() => onImageDelete()}
      >
        Supprimer l’image
      </button>
      <button
        type="button"
        aria-label="Importer"
        onClick={() =>
          onImageUpload(
            { imageFile: new File([''], 'img.png'), credit: null },
            'Votre image a bien été importée'
          )
        }
      >
        Importer
      </button>
    </div>
  ),
}))

const renderButtonImageEdit = (props: ButtonImageEditProps) =>
  renderWithProviders(<ButtonImageEdit {...props} />)

describe('ButtonImageEdit', () => {
  let props: ButtonImageEditProps
  beforeEach(() => {
    props = {
      mode: UploaderModeEnum.OFFER,
      onImageUpload: vi.fn(),
      onImageDelete: vi.fn(),
      onClickButtonImage: vi.fn(),
    }
  })

  it('should render add button', async () => {
    renderButtonImageEdit(props)
    expect(
      await screen.findByRole('button', {
        name: /Ajouter une image/,
      })
    ).toBeInTheDocument()
  })

  it('should render edit button', async () => {
    props = {
      ...props,
      initialValues: {
        ...props.initialValues,
        croppedImageUrl: 'https://test.url',
      },
    }
    renderButtonImageEdit(props)
    expect(
      await screen.findByRole('button', {
        name: /Modifier/,
      })
    ).toBeInTheDocument()
  })

  it('calls onClickButtonImage when clicking on add button', async () => {
    renderButtonImageEdit(props)

    const addButton = await screen.findByRole('button', {
      name: /Ajouter une image/,
    })
    await userEvent.click(addButton)

    expect(props.onClickButtonImage).toHaveBeenCalledTimes(1)
  })

  it('shows success snackbar when uploading image', async () => {
    renderButtonImageEdit(props)

    await userEvent.click(screen.getByRole('button', { name: /Importer/ }))

    expect(props.onImageUpload).toHaveBeenCalledTimes(1)
    expect(snackBarSuccess).toHaveBeenCalledWith(
      'Votre image a bien été importée'
    )
  })

  it('shows error snackbar and not success when onImageUpload throws', async () => {
    props.onImageUpload = vi.fn().mockImplementation(() => {
      throw new Error('Upload failed')
    })
    renderButtonImageEdit(props)

    await userEvent.click(screen.getByRole('button', { name: /Importer/ }))

    expect(snackBarError).toHaveBeenCalledWith(
      "Une erreur est survenue lors de l'importation de votre image"
    )
    expect(snackBarSuccess).not.toHaveBeenCalled()
  })
})
