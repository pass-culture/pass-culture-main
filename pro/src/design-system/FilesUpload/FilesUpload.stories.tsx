import type { Meta, StoryObj } from '@storybook/react-vite'
import { useState } from 'react'
import { Controller, useForm } from 'react-hook-form'

import { Button } from '@/design-system/Button/Button'

import { FilesUpload, type FilesUploadProps } from './FilesUpload'

const createFile = (name: string, size: number) =>
  new File([new Uint8Array(size)], name, { type: 'application/pdf' })

const ControlledFilesUpload = ({
  initialFiles = [],
  ...props
}: FilesUploadProps & { initialFiles?: File[] }) => {
  const [files, setFiles] = useState(initialFiles)

  return <FilesUpload {...props} value={files} onChange={setFiles} />
}

const meta: Meta<typeof FilesUpload> = {
  title: '@/design-system/FilesUpload',
  component: FilesUpload,
  args: {
    label: 'Label qui peut être long voir très long',
    description: 'Description qui peut aussi être très très longue',
    accept: {
      'image/png': ['.png'],
      'image/jpeg': ['.jpeg'],
      'application/pdf': ['.pdf'],
    },
    maxSize: 5_000_000,
    maxFiles: 3,
  },
  decorators: [
    (Story) => (
      <div style={{ maxWidth: 512 }}>
        <Story />
      </div>
    ),
  ],
}

export default meta

type Story = StoryObj<typeof FilesUpload>

export const Default: Story = {}

export const WithFiles: Story = {
  render: (args) => (
    <ControlledFilesUpload
      {...args}
      initialFiles={[
        createFile('Nom du fichier.pdf', 3_000_000),
        createFile('Autre fichier.pdf', 1_200_000),
      ]}
    />
  ),
}

export const WithStatuses: Story = {
  render: (args) => (
    <ControlledFilesUpload
      {...args}
      initialFiles={[
        createFile('Fichier sans statut.pdf', 3_000_000),
        createFile('Fichier envoyé.pdf', 3_000_000),
        createFile('Fichier en erreur.pdf', 3_000_000),
      ]}
      getFileStatus={(file) => {
        if (file.name === 'Fichier envoyé.pdf') {
          return 'success'
        }
        if (file.name === 'Fichier en erreur.pdf') {
          return 'error'
        }
        return undefined
      }}
    />
  ),
}

export const MaxFilesReached: Story = {
  args: {
    maxFiles: 2,
  },
  render: (args) => (
    <ControlledFilesUpload
      {...args}
      initialFiles={[
        createFile('Premier fichier.pdf', 3_000_000),
        createFile('Second fichier.pdf', 3_000_000),
      ]}
    />
  ),
}

export const Disabled: Story = {
  args: {
    disabled: true,
  },
  render: (args) => (
    <ControlledFilesUpload
      {...args}
      initialFiles={[createFile('Nom du fichier.pdf', 3_000_000)]}
    />
  ),
}

const FilesUploadForm = (args: FilesUploadProps) => {
  const [submittedFiles, setSubmittedFiles] = useState<File[]>()
  const { control, handleSubmit } = useForm<{ documents: File[] }>({
    defaultValues: { documents: [] },
  })

  return (
    <form
      onSubmit={handleSubmit(({ documents }) => setSubmittedFiles(documents))}
      style={{ display: 'flex', flexDirection: 'column', gap: 16 }}
    >
      <Controller
        control={control}
        name="documents"
        rules={{
          validate: (documents) =>
            documents.length > 0 || 'Veuillez ajouter au moins un fichier.',
        }}
        render={({ field, fieldState }) => (
          <FilesUpload
            {...args}
            {...field}
            required
            error={fieldState.error?.message}
          />
        )}
      />
      <Button type="submit" label="Envoyer" />
      {submittedFiles && (
        <p>
          Fichiers envoyés :{' '}
          {submittedFiles.map((file) => file.name).join(', ') || 'aucun'}
        </p>
      )}
    </form>
  )
}

export const WithReactHookForm: Story = {
  render: (args) => <FilesUploadForm {...args} />,
}
