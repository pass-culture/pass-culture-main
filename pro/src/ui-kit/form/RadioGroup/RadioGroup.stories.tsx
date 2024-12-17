import { Formik } from 'formik'

import { RadioVariant } from '../shared/BaseRadio/BaseRadio'

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
  name: 'name',
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
}

export const Default = {
  args: defaultArgs,
}

export const WithBorder = {
  args: {
    ...defaultArgs,
    variant: RadioVariant.BOX,
    name: 'name 2',
  },
}

export const WithChildren = {
  args: {
    ...defaultArgs,
    variant: RadioVariant.BOX,
    group: defaultArgs.group.map((g, i) => ({
      ...g,
      childrenOnChecked: <p>Sub content {i}</p>,
    })),
    name: 'name 3',
  },
}
