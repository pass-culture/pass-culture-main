import type { Meta, StoryObj } from '@storybook/react'
import { PropsWithChildren } from 'react'
import { FormProvider, useForm, useFormContext } from 'react-hook-form'

import { Slider, SliderProps } from './Slider'

const meta: Meta<typeof Slider> = {
  title: '@/ui-kit/Slider',
  component: Slider,
}

const Wrapper = ({ children }: PropsWithChildren) => {
  const hookForm = useForm<SliderProps>({
    defaultValues: { scale: 'km' },
  })

  return (
    <FormProvider {...hookForm}>
      <form>{children}</form>
    </FormProvider>
  )
}
export default meta
type Story = StoryObj<typeof Slider>

export const Default: Story = {
  args: {
    name: 'myField',
    scale: 'km',
    onChange: () => {
      //  Control the result here with e.target.value
    },
  },
  decorators: [
    (Story) => {
      return (
        <div style={{ padding: '2rem' }}>
          <Story />
        </div>
      )
    },
  ],
}

export const WithinForm: Story = {
  args: {
    name: 'myField',
    scale: 'km',
  },
  decorators: [
    (Story) => (
      <div style={{ width: 300, height: 300 }}>
        <Wrapper>
          <Story />
        </Wrapper>
      </div>
    ),
  ],
  render: (args) => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const { register } = useFormContext<{ myField: number }>()

    return <Slider {...args} {...register('myField')} />
  },
}
