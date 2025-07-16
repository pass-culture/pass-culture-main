import { StoryObj } from '@storybook/react'

import imageDemo from '../assets/dog.jpg'

import { RadioButtonGroup } from './RadioButtonGroup'

export default {
  title: 'design-system/RadioButtonGroup',
  component: RadioButtonGroup,
}

const options = [
  {
    label: 'Option 1',
    name: 'group1',
    description: 'Description 1',
    value: '1',
  },
  {
    label: 'Option 2',
    name: 'group1',
    description: 'Description 2',
    value: '2',
  },
  {
    label: 'Option 3',
    name: 'group1',
    description: 'Description 3',
    value: '3',
  },
]

export const Default: StoryObj<typeof RadioButtonGroup> = {
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group',
    options,
  },
}

export const Detailed: StoryObj<typeof RadioButtonGroup> = {
  args: {
    name: 'radio-button-group',
    label: 'Detailed Radio Button Group',
    variant: 'detailed',
    options,
  },
}

export const FilledHorizontalDisplay: StoryObj<typeof RadioButtonGroup> = {
  args: {
    name: 'radio-button-group',
    label: 'Horizontal Radio Button Group',
    variant: 'detailed',
    display: 'horizontal',
    sizing: 'fill',
    options,
  },
}

export const HuggedHorizontalDisplay: StoryObj<typeof RadioButtonGroup> = {
  args: {
    name: 'radio-button-group',
    label: 'Hugged Horizontal Radio Button Group',
    variant: 'detailed',
    display: 'horizontal',
    sizing: 'hug',
    options,
  },
}

export const Disabled: StoryObj<typeof RadioButtonGroup> = {
  args: {
    name: 'radio-button-group',
    label: 'Disabled Radio Button Group',
    disabled: true,
    variant: 'detailed',
    options,
  },
}

export const WithDescription: StoryObj<typeof RadioButtonGroup> = {
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Description',
    description: 'This is a description for the radio button group.',
    options,
  },
}

export const WithHeadingTag: StoryObj<typeof RadioButtonGroup> = {
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Heading Tag',
    labelTag: 'h2',
    options,
  },
}

export const WithSpanTag: StoryObj<typeof RadioButtonGroup> = {
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Span Tag',
    labelTag: 'span',
    options,
  },
}

export const WithError: StoryObj<typeof RadioButtonGroup> = {
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Error',
    error: 'This is an error message.',
    options,
  },
}

export const WithCommonAsset: StoryObj<typeof RadioButtonGroup> = {
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Common Asset',
    variant: 'detailed',
    asset: {
      variant: 'image',
      src: imageDemo,
      size: 's',
    },
    options,
  },
}
