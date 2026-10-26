import type { Meta, StoryObj } from '@storybook/react-vite'

import fullDownloadIcon from '@/icons/full-download.svg'

import { UploadZone } from './UploadZone'

const meta: Meta<typeof UploadZone> = {
  title: '@/design-system/UploadZone',
  component: UploadZone,
  args: {
    label: 'Label qui peut être long voir très long',
    accept: {
      'image/png': ['.png'],
      'image/jpeg': ['.jpeg'],
      'application/pdf': ['.pdf'],
    },
    maxSize: 5_000_000,
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

type Story = StoryObj<typeof UploadZone>

export const Default: Story = {}

export const WithDescription: Story = {
  args: {
    description: 'Description qui peut aussi être très très longue',
  },
}

export const LabelTitle3: Story = {
  args: {
    labelVariant: 'title3',
    description: 'Description qui peut aussi être très très longue',
  },
}

export const WithoutLabel: Story = {
  args: {
    label: undefined,
  },
}

export const RequiredSymbol: Story = {
  args: {
    required: true,
    requiredIndicator: 'symbol',
  },
}

export const RequiredExplicit: Story = {
  args: {
    required: true,
    requiredIndicator: 'explicit',
  },
}

export const Disabled: Story = {
  args: {
    disabled: true,
  },
}

export const WithError: Story = {
  args: {
    error: 'Veuillez ajouter un fichier.',
  },
}

export const CustomIcon: Story = {
  args: {
    icon: fullDownloadIcon,
  },
}
