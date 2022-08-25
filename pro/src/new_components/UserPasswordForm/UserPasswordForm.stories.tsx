import type { Story } from '@storybook/react'
import React from 'react'

import { PostPasswordAdapter } from 'routes/User/adapters/postPasswordAdapter'

// storybook doc : https://storybook.js.org/docs/react/writing-stories/introduction

import { UserPasswordForm } from '.'

type Props = React.ComponentProps<typeof UserPasswordForm>

const onFormSubmit = (values: any) => {
  return new Promise(resolve => setTimeout(() => resolve(values), 500))
}

const Template: Story<Props> = args => <UserPasswordForm {...args} />

export const BasicUserPasswordForm = Template.bind({})
BasicUserPasswordForm.storyName = 'Basic Form'
BasicUserPasswordForm.args = {
  postPasswordAdapter: onFormSubmit as PostPasswordAdapter,
}

export const BanneredUserPasswordForm = Template.bind({})
BanneredUserPasswordForm.storyName = 'Bannered Form'
BanneredUserPasswordForm.args = {
  postPasswordAdapter: onFormSubmit as PostPasswordAdapter,
}

export default {
  title: 'components/UserPasswordForm',
}
