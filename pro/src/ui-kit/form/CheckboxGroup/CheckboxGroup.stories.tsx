import { Formik } from 'formik'

import { CheckboxGroup } from './CheckboxGroup'

export default {
  title: 'ui-kit/forms/CheckboxGroup',
  component: CheckboxGroup,
  decorators: [
    (Story: any) => (
      <Formik initialValues={{ accessibility: false }} onSubmit={() => {}}>
        {({ getFieldProps }) => {
          return <Story {...getFieldProps('group')} />
        }}
      </Formik>
    ),
  ],
}

export const Default = {
  args: {
    group: ['foo', 'bar', 'baz'].map((item) => ({
      label: item,
      name: `checkBoxes.${item}`,
    })),
    groupName: 'checkBoxes',
    legend: 'This is the legend',
  },
}
