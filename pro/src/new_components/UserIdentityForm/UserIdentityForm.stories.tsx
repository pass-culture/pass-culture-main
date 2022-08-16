import type { Story } from '@storybook/react'
import React from 'react'

import { PatchIdentityAdapter } from 'routes/User/adapters/patchIdentityAdapter'

// storybook doc : https://storybook.js.org/docs/react/writing-stories/introduction

import { UserIdentityForm } from './'

type Props = React.ComponentProps<typeof UserIdentityForm>

const onFormSubmit = (values: any) => {
  return new Promise(resolve => setTimeout(() => resolve(values), 500))
}

const Template: Story<Props> = args => <UserIdentityForm {...args} />

export const BasicUserIdentityForm = Template.bind({})
BasicUserIdentityForm.storyName = 'Basic Form'
BasicUserIdentityForm.args = {
  patchIdentityAdapter: onFormSubmit as PatchIdentityAdapter,
  initialValues: { firstName: 'Harry', lastName: 'Potter' },
}

export const BanneredUserIdentityForm = Template.bind({})
BanneredUserIdentityForm.storyName = 'Bannered Form'
BanneredUserIdentityForm.args = {
  patchIdentityAdapter: onFormSubmit as PatchIdentityAdapter,
  initialValues: { firstName: 'Harry', lastName: 'Potter' },
}

export default {
  title: 'components/UserIdentityForm',
}
