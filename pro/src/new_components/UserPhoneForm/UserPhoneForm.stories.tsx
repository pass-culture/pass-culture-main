import type { Story } from '@storybook/react'
import React from 'react'

import { PatchPhoneAdapter } from 'routes/User/adapters/patchPhoneAdapter'

// storybook doc : https://storybook.js.org/docs/react/writing-stories/introduction

import { UserPhoneForm } from './'

type Props = React.ComponentProps<typeof UserPhoneForm>

const onFormSubmit = (values: any) => {
  return new Promise(resolve => setTimeout(() => resolve(values), 500))
}

const Template: Story<Props> = args => <UserPhoneForm {...args} />

export const BasicUserPhoneForm = Template.bind({})
BasicUserPhoneForm.storyName = 'Basic Form'
BasicUserPhoneForm.args = {
  patchPhoneAdapter: onFormSubmit as PatchPhoneAdapter,
  initialValues: { phoneNumber: '+3361234567' },
}

export const BanneredUserPhoneForm = Template.bind({})
BanneredUserPhoneForm.storyName = 'Bannered Form'
BanneredUserPhoneForm.args = {
  patchPhoneAdapter: onFormSubmit as PatchPhoneAdapter,
  initialValues: { phoneNumber: '+3361234567' },
}

export default {
  title: 'components/UserPhoneForm',
}
