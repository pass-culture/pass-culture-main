import { Story } from '@storybook/react'
import React, { useState } from 'react'

import { CreditInput } from './CreditInput'

export default {
  title: 'components/CreditInput',
  component: CreditInput,
}

const Template: Story = () => {
  const [credit, setCredit] = useState('')

  return <CreditInput credit={credit} updateCredit={setCredit} />
}

export const Default = Template.bind({})
Default.args = {}
