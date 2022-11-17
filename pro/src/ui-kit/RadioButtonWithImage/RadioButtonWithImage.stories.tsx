import type { Story } from '@storybook/react'
import React, { useState } from 'react'

import { ReactComponent as CaseIcon } from 'icons/ico-case.svg'
import { ReactComponent as PhoneIcon } from 'icons/info-phone.svg'

import RadioButtonWithImage, {
  IRadioButtonWithImage,
} from './RadioButtonWithImage'

export default {
  title: 'ui-kit/RadioButtonWithImage',
  component: RadioButtonWithImage,
}

const Template: Story<IRadioButtonWithImage> = () => {
  const [offerType, setOfferType] = useState('indiv')
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) =>
    setOfferType(e.target.value)
  return (
    <div style={{ maxWidth: '240px' }}>
      <RadioButtonWithImage
        name="offer"
        label="Offre Individuelle"
        isChecked={offerType == 'indiv'}
        onChange={handleChange}
        Icon={PhoneIcon}
        value="indiv"
      />
      <RadioButtonWithImage
        name="collectiveOffer"
        label="Offre Collective"
        isChecked={offerType == 'collective'}
        onChange={handleChange}
        Icon={CaseIcon}
        value="collective"
      />
    </div>
  )
}

export const Default = Template.bind({})
