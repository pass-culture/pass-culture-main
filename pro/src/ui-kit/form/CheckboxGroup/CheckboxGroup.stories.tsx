import { Formik } from 'formik'

import { CheckboxVariant } from '../shared/BaseCheckbox/BaseCheckbox'

import { CheckboxGroup } from './CheckboxGroup'

export default {
  title: 'ui-kit/forms/CheckboxGroup',
  component: CheckboxGroup,
  decorators: [
    (Story: any) => (
      <Formik
        initialValues={{
          checkBoxes: {
            foo: true,
            bar: false,
            baz: false,
            'sub-foo-0': true,
            'sub-bar-0': false,
            'sub-foo-1': false,
            'sub-bar-1': false,
            'sub-foo-2': false,
            'sub-bar-2': false,
          },
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
    group: ['foo', 'bar', 'baz'].map((item) => ({
      label: item,
      name: `checkBoxes.${item}`,
    })),
    groupName: 'checkBoxes',
    legend: 'This is the legend',
    disabled: false,
  },
}

export const Box = {
  args: {
    ...Default.args,
    variant: CheckboxVariant.BOX,
  },
}

export const BoxInline = {
  args: {
    ...Default.args,
    inline: true,
    variant: CheckboxVariant.BOX,
  },
}

export const BoxWithChildren = {
  args: {
    ...Default.args,
    group: ['foo', 'bar', 'baz'].map((item) => ({
      label: item,
      name: `checkBoxes.${item}`,
      childrenOnChecked: <span>Child content for {item}</span>,
    })),
    variant: CheckboxVariant.BOX,
  },
}

export const BoxWithCheckboxGroupChildren = {
  args: {
    ...Default.args,
    group: ['foo', 'bar', 'baz'].map((item, i) => ({
      label: item,
      name: `checkBoxes.${item}`,
      childrenOnChecked: (
        <CheckboxGroup
          legend="Sub group legend"
          groupName="sub-name"
          group={[
            { label: 'sub-foo', name: `checkBoxes.sub-foo-${i}` },
            { label: 'sub-bar', name: `checkBoxes.sub-bar-${i}` },
          ]}
          variant={CheckboxVariant.BOX}
        />
      ),
    })),
    variant: CheckboxVariant.BOX,
  },
}

export const BoxWithCheckboxGroupChildrenNoLegend = {
  args: {
    ...Default.args,
    group: ['foo', 'bar', 'baz'].map((item, i) => ({
      label: <span>{item}</span>,
      name: `checkBoxes.${item}`,
      childrenOnChecked: (
        <CheckboxGroup
          describedBy="parent-name-id"
          groupName="sub-name"
          group={[
            { label: 'sub-foo', name: `checkBoxes.sub-foo-${i}` },
            { label: 'sub-bar', name: `checkBoxes.sub-bar-${i}` },
          ]}
          variant={CheckboxVariant.BOX}
          inline={i === 0}
        />
      ),
    })),
    variant: CheckboxVariant.BOX,
  },
}

export const BoxWithCheckboxGroupChildrenDisabled = {
  args: {
    ...Default.args,
    disabled: true,
    group: ['foo', 'bar', 'baz'].map((item, i) => ({
      label: <span>{item}</span>,
      name: `checkBoxes.${item}`,
      childrenOnChecked: (
        <CheckboxGroup
          describedBy="parent-name-id"
          groupName="sub-name"
          group={[
            { label: 'sub-foo', name: `checkBoxes.sub-foo-${i}` },
            { label: 'sub-bar', name: `checkBoxes.sub-bar-${i}` },
          ]}
          variant={CheckboxVariant.BOX}
          inline={i === 0}
          disabled={true}
        />
      ),
    })),
    variant: CheckboxVariant.BOX,
    groupName: 'checkBoxes',
    legend: 'This is the legend',
  },
}
