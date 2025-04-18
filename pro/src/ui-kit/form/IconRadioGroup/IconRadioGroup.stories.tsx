import { FormProvider, useForm } from 'react-hook-form'

import { IconRadioGroup } from 'ui-kit/form/IconRadioGroup/IconRadioGroup'

export default {
  title: 'ui-kit/forms/IconRadioGroup',
  component: IconRadioGroup,
}

const group = [
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
]

export const Default = {
  args: {
    name: 'question',
    legend: 'What is the question?',
    group: group,
    value: '1',
    onChange: () => {},
  },
}

export const WithError = {
  args: {
    name: 'question',
    legend: 'What is the question?',
    error: 'This is an error message',
    group: group,
    value: '1',
    onChange: () => {},
  },
}

export const WithinForm = {
  args: {
    name: 'group',
    legend: 'Choisir une option',
  },
  render: (args: any) => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const hookForm = useForm<{ question: string }>({
      defaultValues: { question: '1' },
    })

    return (
      <FormProvider {...hookForm}>
        <form>
          <IconRadioGroup
            {...args}
            group={group}
            value={hookForm.watch('question')}
            onChange={(val) => hookForm.setValue('question', val)}
          ></IconRadioGroup>
        </form>
      </FormProvider>
    )
  },
}
