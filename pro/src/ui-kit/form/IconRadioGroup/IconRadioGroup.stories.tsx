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

export const Default = {
  args: {
    name: 'question',
    legend: 'What is the question?',
    group: [
      {
        label: 'Mécontent',
        icon: 'J',
        value: '1',
      },
      {
        label: 'Content',
        icon: <span>2</span>,
        value: '2',
      },
      {
        label: 'Très Content',
        icon: <span>3</span>,
        value: '3',
      },
    ],
  },
}
