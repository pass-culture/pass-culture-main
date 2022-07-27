import { Story } from '@storybook/react'
import React from 'react'

import { ResetEmailBanner } from 'new_components/Banner'
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
  title: 'Are you a wizard ?',
  subtitleFormat: () => 'Harry Potter',
  patchIdentityAdapter: onFormSubmit as PatchIdentityAdapter,
  initialValues: { firstName: 'Harry', lastName: 'Potter' },
}

export const BanneredUserIdentityForm = Template.bind({})
BanneredUserIdentityForm.storyName = 'Bannered Form'
BanneredUserIdentityForm.args = {
  title: 'Are you a wizard ?',
  subtitleFormat: () => 'Harry Potter',
  patchIdentityAdapter: onFormSubmit as PatchIdentityAdapter,
  initialValues: { firstName: 'Harry', lastName: 'Potter' },
  shouldDisplayBanner: true,
  banner: <ResetEmailBanner email="harry.socier15ans@poudlar.com" />,
}

export default {
  title: 'components/UserIdentityForm',
}
