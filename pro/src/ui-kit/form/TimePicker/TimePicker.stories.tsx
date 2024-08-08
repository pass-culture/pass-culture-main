import { StoryObj } from '@storybook/react'
import { Formik } from 'formik'

import { TimePicker } from './TimePicker'

export default {
  title: 'ui-kit/forms/TimePicker',
  component: TimePicker,
  decorators: [
    (Story: any) => (
      <Formik initialValues={{ time: null }} onSubmit={() => {}}>
        <Story />
      </Formik>
    ),
  ],
}

export const WithClearButton: StoryObj<typeof TimePicker> = {
  args: {
    name: 'time',
    label: 'Horaire',
    clearButtonProps: {
      tooltip: "Supprimer l'horaire",
      onClick: () => alert('Clear !'),
    },
  },
}

export const WithoutLabel: StoryObj<typeof TimePicker> = {
  args: { name: 'time' },
}

export const WithLabel: StoryObj<typeof TimePicker> = {
  args: {
    name: 'time',
    label: 'Horaire',
  },
}

export const FilterVariant: StoryObj<typeof TimePicker> = {
  args: {
    name: 'time',
    filterVariant: true,
  },
}

export const WithoutSuggestList: StoryObj<typeof TimePicker> = {
  args: {
    name: 'time',
    showIntervalList: false,
  },
}
