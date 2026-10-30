import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Controller, useForm } from 'react-hook-form'
import { axe } from 'vitest-axe'

import { FilesUpload, type FilesUploadProps } from './FilesUpload'

const defaultProps: FilesUploadProps = {
  label: 'Justificatifs',
  accept: { 'application/pdf': ['.pdf'] },
  maxSize: 5_000_000,
  maxFiles: 3,
}

function renderFilesUpload(props?: Partial<FilesUploadProps>) {
  return render(
    <FilesUpload {...defaultProps} {...(props as FilesUploadProps)} />
  )
}

function createFile(name: string) {
  return new File(['content'], name, { type: 'application/pdf' })
}

const getInput = () => screen.getByLabelText('Justificatifs')
const getFileNames = () =>
  within(screen.getByRole('list', { name: 'Fichiers ajoutés' }))
    .getAllByRole('listitem')
    .map((item) => item.querySelector('p')?.textContent)

describe('FilesUpload', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderFilesUpload({
      value: [createFile('a.pdf'), createFile('b.pdf')],
      getFileStatus: (file) => (file.name === 'a.pdf' ? 'success' : 'error'),
    })

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should not display the files list without files', () => {
    renderFilesUpload()

    expect(screen.queryByRole('list')).not.toBeInTheDocument()
    expect(screen.getByText('0/3 fichiers maximum')).toBeInTheDocument()
  })

  it('should add the selected files to the list', async () => {
    const onChange = vi.fn()
    renderFilesUpload({ onChange })
    const fileA = createFile('a.pdf')
    const fileB = createFile('b.pdf')

    await userEvent.upload(getInput(), [fileA])
    await userEvent.upload(getInput(), [fileB])

    expect(getFileNames()).toEqual(['a.pdf', 'b.pdf'])
    expect(screen.getByText('2/3 fichiers maximum')).toBeInTheDocument()
    expect(onChange).toHaveBeenLastCalledWith([fileA, fileB])
  })

  it('should display the status of each file', () => {
    renderFilesUpload({
      value: [createFile('a.pdf'), createFile('b.pdf')],
      getFileStatus: (file) => (file.name === 'a.pdf' ? 'success' : 'error'),
    })

    const [itemA, itemB] = screen.getAllByRole('listitem')
    expect(within(itemA).getByRole('status')).toHaveTextContent(
      'Fichier ajouté'
    )
    expect(within(itemB).getByRole('status')).toHaveTextContent(
      'Une erreur est survenue. Veuillez télécharger à nouveau le fichier.'
    )
  })

  it('should disable the upload zone when the maximum number of files is reached', async () => {
    renderFilesUpload({ maxFiles: 2 })

    await userEvent.upload(getInput(), [
      createFile('a.pdf'),
      createFile('b.pdf'),
    ])

    expect(getInput()).toHaveAttribute('aria-disabled', 'true')
    expect(screen.getByText('2/2 fichiers maximum')).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', { name: 'Supprimer a.pdf' })
    )

    expect(getInput()).not.toHaveAttribute('aria-disabled')
  })

  it('should disable the upload zone and the delete buttons', () => {
    renderFilesUpload({ value: [createFile('a.pdf')], disabled: true })

    expect(getInput()).toBeDisabled()
    expect(
      screen.getByRole('button', { name: 'Supprimer a.pdf' })
    ).toBeDisabled()
  })

  describe('when deleting a file', () => {
    const files = ['a.pdf', 'b.pdf', 'c.pdf'].map(createFile)

    it('should remove the file and focus the next one', async () => {
      const onChange = vi.fn()
      renderFilesUpload({ onChange })
      await userEvent.upload(getInput(), files)

      await userEvent.click(
        screen.getByRole('button', { name: 'Supprimer b.pdf' })
      )

      expect(getFileNames()).toEqual(['a.pdf', 'c.pdf'])
      expect(onChange).toHaveBeenLastCalledWith([files[0], files[2]])
      expect(
        screen.getByRole('button', { name: 'Supprimer c.pdf' })
      ).toHaveFocus()
    })

    it('should focus the previous file when deleting the last one', async () => {
      renderFilesUpload()
      await userEvent.upload(getInput(), files)

      await userEvent.click(
        screen.getByRole('button', { name: 'Supprimer c.pdf' })
      )

      expect(
        screen.getByRole('button', { name: 'Supprimer b.pdf' })
      ).toHaveFocus()
    })

    it('should focus the upload zone when deleting the only file', async () => {
      renderFilesUpload()
      await userEvent.upload(getInput(), [files[0]])

      await userEvent.click(
        screen.getByRole('button', { name: 'Supprimer a.pdf' })
      )

      expect(screen.queryByRole('list')).not.toBeInTheDocument()
      expect(getInput()).toHaveFocus()
    })
  })

  describe('in a react-hook-form form', () => {
    const onSubmit = vi.fn()

    const TestForm = () => {
      const { control, handleSubmit } = useForm<{ documents: File[] }>({
        defaultValues: { documents: [] },
      })

      return (
        <form onSubmit={handleSubmit(onSubmit)}>
          <Controller
            control={control}
            name="documents"
            rules={{
              validate: (documents) =>
                documents.length > 0 || 'Veuillez ajouter un fichier',
            }}
            render={({ field, fieldState }) => (
              <FilesUpload
                {...defaultProps}
                {...field}
                error={fieldState.error?.message}
              />
            )}
          />
          <button type="submit">Envoyer</button>
        </form>
      )
    }

    it('should give the selected files on submit', async () => {
      render(<TestForm />)
      const files = ['a.pdf', 'b.pdf', 'c.pdf'].map(createFile)

      await userEvent.upload(getInput(), files)
      await userEvent.click(
        screen.getByRole('button', { name: 'Supprimer b.pdf' })
      )
      await userEvent.click(screen.getByRole('button', { name: 'Envoyer' }))

      expect(onSubmit).toHaveBeenCalledWith(
        { documents: [files[0], files[2]] },
        expect.anything()
      )
    })

    it('should display the form error and focus the upload zone', async () => {
      render(<TestForm />)

      await userEvent.click(screen.getByRole('button', { name: 'Envoyer' }))

      expect(screen.getByRole('alert')).toHaveTextContent(
        'Veuillez ajouter un fichier'
      )
      expect(getInput()).toHaveFocus()
      expect(onSubmit).not.toHaveBeenCalled()
    })
  })
})
