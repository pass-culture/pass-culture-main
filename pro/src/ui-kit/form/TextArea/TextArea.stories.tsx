import type { Meta, StoryObj } from '@storybook/react'
import { PropsWithChildren } from 'react'
import { FormProvider, useForm, useFormContext } from 'react-hook-form'

import { TextArea } from './TextArea'

const Wrapper = ({ children }: PropsWithChildren) => {
  const hookForm = useForm<{ myField: string }>({
    defaultValues: { myField: 'default value' },
  })

  return (
    <FormProvider {...hookForm}>
      <form>{children}</form>
    </FormProvider>
  )
}

const meta: Meta<typeof TextArea> = {
  title: 'ui-kit/formsV2/TextArea',
  component: TextArea,
}

export default meta
type Story = StoryObj<typeof TextArea>

export const Default: Story = {
  args: {
    name: 'description',
    label: 'Description',
    required: true,
  },
}

export const WithError: Story = {
  args: {
    name: 'description',
    label: 'Description',
    error: 'This is an error',
  },
}

export const WithInitialHeight: Story = {
  args: {
    name: 'description',
    label: 'Description',
    initialRows: 20,
  },
}

export const Disabled: Story = {
  args: {
    name: 'description',
    label: 'Description',
    disabled: true,
  },
}

export const WithGeneratedTemplate: Story = {
  args: {
    name: 'description',
    label: 'Description',
    hasTemplateButton: true,
    wordingTemplate: 'Template content...',
    onPressTemplateButton: () => {},
  },
}

export const WithinForm: Story = {
  args: {
    name: 'description',
    label: 'Description',
  },
  decorators: [
    (Story: any) => (
      <Wrapper>
        <Story />
      </Wrapper>
    ),
  ],
  render: (args: any) => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const { setValue, watch } = useFormContext<{ myField: string }>()

    return (
      <TextArea
        {...args}
        value={watch('myField')}
        onChange={(e) => {
          setValue('myField', e.target.value)
        }}
      ></TextArea>
    )
  },
}
