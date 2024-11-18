import { Formik } from 'formik'

import { IconRadioGroup } from 'ui-kit/form/IconRadioGroup/IconRadioGroup'

export default {
  title: 'ui-kit/forms/IconRadioGroup',
  component: IconRadioGroup,
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
  args: {
    name: 'question',
    legend: 'What is the question?',
    group: [
      {
        label: 'This should be hidden',
        icon: 'J',
        value: '1',
      },
      {
        label: 'This should be hidden too',
        icon: <span>2</span>,
        value: '2',
      },
    ],
  },
}
