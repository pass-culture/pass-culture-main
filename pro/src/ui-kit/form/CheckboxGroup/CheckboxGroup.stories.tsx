import { FormProvider, useForm } from 'react-hook-form'

import { CheckboxGroup, type CheckboxGroupProps } from './CheckboxGroup'

export default {
  title: '@/ui-kit/formsV2/CheckboxGroup',
  component: CheckboxGroup,
}

const defaultArgs = {
  name: 'group',
  legend: 'Choisir une option',
  group: [
    {
      label: 'checkbox 1',
      onChange: () => {},
      checked: true,
    },
    {
      label: 'checkbox 2',
      onChange: () => {},
      checked: false,
    },
  ],
} satisfies CheckboxGroupProps

export const Default = {
  args: defaultArgs,
}

export const WithinForm = {
  args: {
    name: 'group',
    legend: 'Choisir une option',
  },
  render: (args: CheckboxGroupProps) => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const hookForm = useForm<{ checkbox1: boolean; checkbox2: boolean }>({
      defaultValues: { checkbox1: true, checkbox2: false },
    })

    return (
      <FormProvider {...hookForm}>
        <form>
          <CheckboxGroup
            {...args}
            group={[
              {
                label: 'checkbox 1',
                checked: hookForm.watch('checkbox1'),
                onChange: (e) => {
                  hookForm.setValue('checkbox1', e.target.checked)
                },
              },
              {
                label: 'checkbox 2',
                checked: hookForm.watch('checkbox2'),
                onChange: (e) => {
                  hookForm.setValue('checkbox2', e.target.checked)
                },
              },
            ]}
          ></CheckboxGroup>
        </form>
      </FormProvider>
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
  },
}

export const Inline = {
  args: {
    ...defaultArgs,
    variant: 'detailed',
    inline: true,
  },
}
