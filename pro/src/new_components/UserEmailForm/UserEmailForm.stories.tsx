import type { Story } from '@storybook/react'
import React from 'react'

import { PostEmailAdapter } from 'routes/User/adapters/postEmailAdapter'

// storybook doc : https://storybook.js.org/docs/react/writing-stories/introduction

import { UserEmailForm } from '.'

type Props = React.ComponentProps<typeof UserEmailForm>

const onFormSubmit = (values: any) => {
  return new Promise(resolve => setTimeout(() => resolve(values), 500))
}

const Template: Story<Props> = args => <UserEmailForm {...args} />

export const BasicUserEmailForm = Template.bind({})
BasicUserEmailForm.storyName = 'Basic Form'
BasicUserEmailForm.args = {
  postEmailAdapter: onFormSubmit as PostEmailAdapter,
}

export const BanneredUserEmailForm = Template.bind({})
BanneredUserEmailForm.storyName = 'Bannered Form'
BanneredUserEmailForm.args = {
  postEmailAdapter: onFormSubmit as PostEmailAdapter,
}

export default {
  title: 'components/UserEmailForm',
}
