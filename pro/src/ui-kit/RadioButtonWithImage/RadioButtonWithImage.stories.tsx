import type { Story } from '@storybook/react'
import React, { useState } from 'react'

import CaseIcon from 'icons/ico-case.svg'
import phoneStrokeIcon from 'icons/stroke-phone.svg'

import RadioButtonWithImage, {
  IRadioButtonWithImage,
} from './RadioButtonWithImage'

export default {
  title: 'ui-kit/RadioButtonWithImage',
  component: RadioButtonWithImage,
}

const Template: Story<IRadioButtonWithImage> = ({ description }) => {
  const [offerType, setOfferType] = useState('indiv')
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) =>
    setOfferType(e.target.value)
  return (
    <div style={{ maxWidth: description ? '480px' : '240px' }}>
      <RadioButtonWithImage
        name="offerType"
        label="Offre Individuelle"
        description={description}
        isChecked={offerType == 'indiv'}
        onChange={handleChange}
        icon={phoneStrokeIcon}
        value="indiv"
      />
      <br />
      <RadioButtonWithImage
        name="offerType"
        label="Offre Collective"
        description={description}
        isChecked={offerType == 'collective'}
        onChange={handleChange}
        icon={CaseIcon}
        value="collective"
      />
    </div>
  )
}

export const Default = Template.bind({})
export const WithDescription = Template.bind({})
WithDescription.args = {
  description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit',
}
