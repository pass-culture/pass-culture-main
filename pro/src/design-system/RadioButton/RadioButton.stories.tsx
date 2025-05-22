import { StoryObj } from '@storybook/react'
import { withRouter } from 'storybook-addon-remix-react-router'

import strokeDateIcon from 'icons/stroke-date.svg'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'

import imageDemo from './assets/image-demo.png'
import { RadioButton } from './RadioButton'

/* // This is only to present the component properly in the storybook file.
const RadioButton = (
  props: RadioButtonProps
): ReturnType<typeof OriginalRadioButton> => {
  return (
    <div style={{ margin: 8, display: 'inline-block' }}>
      <OriginalRadioButton {...props} />
    </div>
  )
} */

export default {
  title: 'design-system/RadioButton',
  decorators: [withRouter],
  component: RadioButton,
}

export const Default: StoryObj<typeof RadioButton> = {
  args: {
    name: 'item',
    label: 'Label',
    value: '1',
    variant: 'DEFAULT',
  },
}

export const DefaultDisabled: StoryObj<typeof RadioButton> = {
  render: () => (
    <>
      <RadioButton name="item" label="Label" value="1" disabled />
    </>
  ),
}

export const Detailed: StoryObj<typeof RadioButton> = {
  render: () => (
    <RadioButton variant="DETAILED" name="item" label="Label" value="1" />
  ),
}

export const DetailedWithDescription: StoryObj<typeof RadioButton> = {
  render: () => (
    <RadioButton
      variant="DETAILED"
      name="item"
      label="Label"
      value="1"
      description="Description ou exemple pour préciser"
    />
  ),
}

export const DetailedFullWidth: StoryObj<typeof RadioButton> = {
  render: () => (
    <RadioButton
      variant="DETAILED"
      sizing="FILL"
      name="offer_type"
      label="Individuelle"
      description="Faire une offre pour les jeunes"
      value="1"
    />
  ),
}

export const DetailedWithTag: StoryObj<typeof RadioButton> = {
  render: () => (
    <RadioButton
      variant="DETAILED"
      name="offer_type"
      label="Individuelle"
      description="Faire une offre pour les jeunes"
      tag={<Tag variant={TagVariant.LIGHT_GREY}>Texte</Tag>}
      value="1"
    />
  ),
}

export const DetailedWithIcon: StoryObj<typeof RadioButton> = {
  render: () => (
    <RadioButton
      variant="DETAILED"
      name="date"
      label="Immédiatement"
      description="Au plus rapide selon la charge"
      icon={strokeDateIcon}
      value="today"
    />
  ),
}

export const DetailedWithText: StoryObj<typeof RadioButton> = {
  render: () => (
    <RadioButton
      variant="DETAILED"
      name="price"
      label="Basique"
      description="Fonctionnalités de base"
      text="19€"
      value="1"
    />
  ),
}

export const DetailedWithImage: StoryObj<typeof RadioButton> = {
  render: () => (
    <RadioButton
      variant="DETAILED"
      name="date"
      label="Immédiatement"
      description="Au plus rapide selon la charge"
      image={imageDemo}
      value="today"
    />
  ),
}

export const DetailedWithChildrenOnChecked: StoryObj<typeof RadioButton> = {
  render: () => (
    <RadioButton
      variant="DETAILED"
      name="date"
      label="Immédiatement"
      description="Au plus rapide selon la charge"
      value="today"
      childrenOnChecked={
        <>
          <RadioButton
            variant="DETAILED"
            name="offer_type"
            label="Individuelle"
            description="Faire une offre pour les jeunes"
            value="1"
          />
          <RadioButton
            variant="DETAILED"
            name="offer_type"
            label="Collective"
            description="Faire une offre pour les établissements"
            value="tomorrow"
          />
        </>
      }
      checked
    />
  ),
}
