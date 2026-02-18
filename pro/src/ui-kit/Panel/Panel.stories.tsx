import type { StoryObj } from '@storybook/react-vite'
import { useState } from 'react'
import { useForm } from 'react-hook-form'

import { Panel, PanelProps } from './Panel'

export default {
  title: '@/ui-kit/Panel',
  component: Panel,
}

const DefaultPanel = (args: PanelProps) => {
  const [showForm, setShowForm] = useState(false)

  const methods = useForm({
    defaultValues: { email: '', password: '' },
    mode: 'onChange',
  })

  const {
    handleSubmit,
    formState: { isSubmitting },
  } = methods

  const onSubmit = () => {
    setShowForm(false)
  }

  return (
    <Panel {...args}>
       I am a beautiful panel
    </Panel>
  )
}

export const Default: StoryObj<typeof Panel> = {
  render: () => <DefaultPanel />,
}
