import { Meta, StoryObj } from '@storybook/react'

import dog from '../assets/dog.jpg'

import { CheckboxGroup, CheckboxGroupOption } from './CheckboxGroup'

const defaultOptions: CheckboxGroupOption[] = [
  { label: 'Option 1', value: '1' },
  { label: 'Option 2', value: '2' },
  { label: 'Option 3', value: '3' },
]

const detailedOptions: CheckboxGroupOption[] = [
  {
    label: 'Detailed 1',
    value: 'a',
    variant: 'detailed',
    description: 'Detailed description 1',
    asset: { variant: 'image', src: dog },
  },
  {
    label: 'Detailed 2',
    value: 'b',
    variant: 'detailed',
    description: 'Detailed description 2',
    asset: { variant: 'image', src: dog },
  },
  {
    label: 'Detailed 3',
    value: 'c',
    variant: 'detailed',
    description: 'Detailed description 3',
    asset: { variant: 'image', src: dog },
  },
]

const meta: Meta<typeof CheckboxGroup> = {
  title: 'Design System/CheckboxGroup',
  component: CheckboxGroup,
  tags: ['autodocs'],
}
export default meta

type Story = StoryObj<typeof CheckboxGroup>

export const DefaultVertical: Story = {
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical',
  },
}

export const DefaultHorizontal: Story = {
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'horizontal',
  },
}

export const DefaultWithDescription: Story = {
  args: {
    label: 'Choose your options',
    description: 'You can select several options.',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical',
  },
}

export const DefaultWithError: Story = {
  args: {
    label: 'Choose your options',
    error: 'You must select at least one option.',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical',
  },
}

export const DefaultDisabled: Story = {
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical',
    disabled: true,
  },
}

export const DefaultWithDefaultValue: Story = {
  args: {
    label: 'Choose your options',
    options: defaultOptions,
    variant: 'default',
    display: 'vertical',
    value: ['2'],
  },
}

export const DetailedVertical: Story = {
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical',
  },
}

export const DetailedHorizontal: Story = {
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'horizontal',
  },
}

export const DetailedWithDescription: Story = {
  args: {
    label: 'Choose your detailed options',
    description: 'You can select several options.',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical',
  },
}

export const DetailedWithHeadingTag: Story = {
  args: {
    label: 'Radio Button Group with Heading Tag',
    labelTag: 'h2',
    options: detailedOptions,
    variant: 'detailed',
    description: 'Description with heading',
  },
}

export const DetailedWithSpanTag: Story = {
  args: {
    label: 'Radio Button Group with Span Tag',
    labelTag: 'span',
    options: detailedOptions,
    variant: 'detailed',
    description: 'Description with span',
  },
}

export const DetailedWithError: Story = {
  args: {
    label: 'Choose your detailed options',
    error: 'You must select at least one option.',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical',
  },
}

export const DetailedDisabled: Story = {
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical',
    disabled: true,
  },
}

export const DetailedWithDefaultValue: Story = {
  args: {
    label: 'Choose your detailed options',
    options: detailedOptions,
    variant: 'detailed',
    display: 'vertical',
    value: ['b'],
  },
}
