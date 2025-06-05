import { PropsWithChildren } from 'react'
import { FormProvider, useForm, useFormContext } from 'react-hook-form'

import { RadioGroup, RadioGroupProps } from './RadioGroup'

export default {
  title: 'ui-kit/formsV2/RadioGroup',
  component: RadioGroup,
}

const Wrapper = ({ children }: PropsWithChildren) => {
  const hookForm = useForm<{ group: string }>({
    defaultValues: { group: 'option1' },
  })

  return (
    <FormProvider {...hookForm}>
      <form>{children}</form>
    </FormProvider>
  )
}

const defaultArgs: RadioGroupProps = {
  name: 'group',
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
    {
      label: 'Option 3',
      value: `option3`,
    },
  ],
  onChange: () => {},
}

export const Default = {
  args: defaultArgs,
}

export const WithinForm = {
  args: defaultArgs,
  decorators: [
    (Story: any) => (
      <Wrapper>
        <Story />
      </Wrapper>
    ),
  ],
  render: (args: any) => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const { setValue, watch } = useFormContext<{ group: string }>()

    return (
      <RadioGroup
        {...args}
        checkedOption={watch('group')}
        onChange={(e) => {
          setValue('group', e.target.value)
        }}
      ></RadioGroup>
    )
  },
}

export const Disabled = {
  args: { ...defaultArgs, variant: 'detailed', disabled: true },
}

export const WithBorder = {
  args: {
    ...defaultArgs,
    variant: 'detailed',
    name: 'name 2',
  },
}

export const Inline = {
  args: {
    ...defaultArgs,
    variant: 'detailed',
    displayMode: 'inline',
  },
}

export const InlineGrow = {
  args: {
    ...defaultArgs,
    variant: 'detailed',
    displayMode: 'inline-grow',
  },
}

export const WithChildren = {
  args: {
    ...defaultArgs,
    variant: 'detailed',
    group: defaultArgs.group.map((g, i) => ({
      ...g,
      childrenOnChecked: (
        <RadioGroup
          legend="Choisir une sous-option"
          name="name 4"
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
    variant: 'detailed',
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
    variant: 'detailed',
    group: defaultArgs.group.map((g, i) => ({
      ...g,
      childrenOnChecked: (
        <RadioGroup
          legend="Choisir une sous-option"
          name="name 4"
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
