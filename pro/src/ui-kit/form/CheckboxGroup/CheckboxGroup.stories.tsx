import { Formik } from 'formik'

import { CheckboxGroup } from './CheckboxGroup'
import { CheckboxVariant } from '../shared/BaseCheckbox/BaseCheckbox'

export default {
  title: 'ui-kit/forms/CheckboxGroup',
  component: CheckboxGroup,
  decorators: [
    (Story: any) => (
      <Formik
        initialValues={{ checkBoxes: { foo: true, bar: false, baz: false } }}
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
  },
}

export const Box = {
  args: {
    group: ['foo', 'bar', 'baz'].map((item) => ({
      label: item,
      name: `checkBoxes.${item}`,
    })),
    variant: CheckboxVariant.BOX,
    groupName: 'checkBoxes',
    legend: 'This is the legend',
  },
}

export const BoxInline = {
  args: {
    group: ['foo', 'bar', 'baz'].map((item) => ({
      label: item,
      name: `checkBoxes.${item}`,
    })),
    inline: true,
    variant: CheckboxVariant.BOX,
    groupName: 'checkBoxes',
    legend: 'This is the legend',
  },
}

export const BoxWithChildren = {
  args: {
    group: ['foo', 'bar', 'baz'].map((item) => ({
      label: item,
      name: `checkBoxes.${item}`,
      childrenOnChecked: <span>Child content for {item}</span>,
    })),
    variant: CheckboxVariant.BOX,
    groupName: 'checkBoxes',
    legend: 'This is the legend',
  },
}

export const BoxWithCheckboxGroupChildren = {
  args: {
    group: ['foo', 'bar', 'baz'].map((item) => ({
      label: item,
      name: `checkBoxes.${item}`,
      childrenOnChecked: (
        <CheckboxGroup
          legend="Sub group legend"
          groupName="sub-name"
          group={[
            { label: 'sub-foo', name: 'checkBoxes.sub-foo' },
            { label: 'sub-bar', name: 'checkBoxes.sub-bar' },
          ]}
          variant={CheckboxVariant.BOX}
        />
      ),
    })),
    variant: CheckboxVariant.BOX,
    groupName: 'checkBoxes',
    legend: 'This is the legend',
  },
}

export const BoxWithCheckboxGroupChildrenNoLegend = {
  args: {
    group: ['foo', 'bar', 'baz'].map((item, i) => ({
      label: <span id="parent-name-id">{item}</span>,
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
    groupName: 'checkBoxes',
    legend: 'This is the legend',
  },
}
