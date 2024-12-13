import { Formik } from 'formik'

import { RadioGroup } from './RadioGroup'

export default {
  title: 'ui-kit/forms/RadioGroup',
  component: RadioGroup,
  decorators: [
    (Story: any) => (
      <Formik
        initialValues={{
          question: {},
        }}
        onSubmit={() => {}}
      >
        {({ getFieldProps }) => {
          return <Story {...getFieldProps('group')} />
        }}
      </Formik>
    ),
  ],
}

const defaultArgs = {
  name: 'question',
  legend: 'This is the legend',
  group: [
    {
      label: 'Oui',
      value: `question1`,
    },
    {
      label: 'Non',
      value: `question2`,
    },
  ],
  withBorder: false,
}

export const Default = {
  args: defaultArgs,
}

export const WithBorder = {
  args: {
    ...defaultArgs,
    withBorder: true,
  },
}
