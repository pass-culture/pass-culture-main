import { Formik } from 'formik'

import { DatePicker } from './DatePicker'

export default {
  title: 'ui-kit/forms/DatePicker',
  component: DatePicker,
  decorators: [
    (Story: any) => (
      <Formik initialValues={{ date: '' }} onSubmit={() => {}}>
        <Story />
      </Formik>
    ),
  ],
}

export const WithoutLabel = {
  args: {
    name: 'date',
  },
}

export const WithLabel = {
  args: {
    name: 'date',
    disabled: false,
    label: 'label',
  },
}

export const FilterVariant = {
  args: {
    name: 'date',
    filterVariant: true,
  },
}
