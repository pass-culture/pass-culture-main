import type { StoryObj } from '@storybook/react'
import { Formik } from 'formik'

import { Slider } from './Slider'

export default {
  title: 'ui-kit/forms/Slider',
  component: Slider,
  decorators: [
    (Story: any) => (
      <Formik
        initialValues={{ sliderValue: 0 }}
        onSubmit={() => {}}
        style={{ width: 300, height: 300 }}
      >
        <Story />
      </Formik>
    ),
  ],
}

export const Default: StoryObj<typeof Slider> = {
  args: {
    fieldName: 'sliderValue',
    scale: 'km',
  },
}
