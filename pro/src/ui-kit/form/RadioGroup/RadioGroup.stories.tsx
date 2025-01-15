import { Formik } from 'formik'

import { RadioVariant } from '../shared/BaseRadio/BaseRadio'

import { RadioGroup, RadioGroupProps } from './RadioGroup'

export default {
  title: 'ui-kit/forms/RadioGroup',
  component: RadioGroup,
  decorators: [
    (Story: any) => (
      <Formik
        initialValues={{
          ['name']: 'option1',
          ['name 3']: 'option1',
          ['name 4']: 'option02',
          ['name 5']: 'option3',
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

const defaultArgs: RadioGroupProps = {
  name: 'name',
  legend: 'Choisir une option',
  group: [
    {
      label: 'Option 1',
      value: `option1`,
    },
    {
      label: 'Option 2',
      value: `option2`,
    },
  ],
}

export const Default = {
  args: defaultArgs,
}

export const Disabled = {
  args: { ...defaultArgs, variant: RadioVariant.BOX, disabled: true },
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
      childrenOnChecked: (
        <RadioGroup
          legend="Choisir une sous-option"
          name="name 4"
          variant={RadioVariant.BOX}
          group={[
            { label: `Sous-option ${i + 1} 1`, value: `option${i}1` },
            { label: `Sous-option ${i + 1} 2`, value: `option${i}2` },
          ]}
        />
      ),
    })),
    name: 'name 3',
  },
}

export const InnerRadioGroupWithNoLegend = {
  args: {
    ...defaultArgs,
    variant: RadioVariant.BOX,
    name: 'name 5',
    group: [
      {
        label: <span id="my-id-1">Option 1</span>,
        value: 'option1',
      },
      {
        label: <span id="my-id-2">Option 2</span>,
        value: 'option2',
      },
      {
        label: <span id="my-id-3">Option 3</span>,
        value: 'option3',
        childrenOnChecked: (
          <RadioGroup
            name="subgroup"
            describedBy="my-id-3"
            variant={RadioVariant.BOX}
            group={[
              { label: 'Sous-option 1', value: 'sub-option-1' },
              { label: 'Sous-option 2', value: 'sub-option-2' },
            ]}
          />
        ),
      },
    ],
  },
}

export const WithChildrenDisabled = {
  args: {
    ...defaultArgs,
    disabled: true,
    variant: RadioVariant.BOX,
    group: defaultArgs.group.map((g, i) => ({
      ...g,
      childrenOnChecked: (
        <RadioGroup
          legend="Choisir une sous-option"
          name="name 4"
          variant={RadioVariant.BOX}
          group={[
            { label: `Sous-option ${i + 1} 1`, value: `option${i}1` },
            { label: `Sous-option ${i + 1} 2`, value: `option${i}2` },
          ]}
          disabled={true}
        />
      ),
    })),
    name: 'name 3',
  },
}
