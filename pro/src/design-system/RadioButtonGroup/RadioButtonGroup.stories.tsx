import { StoryObj } from '@storybook/react'
import { useState } from 'react'

import { RadioButton } from '@/design-system/RadioButton/RadioButton'
import { TagVariant } from '@/design-system/Tag/Tag'
import strokeDateIcon from '@/icons/stroke-date.svg'

import imageDemo from '../assets/dog.jpg'
import { RadioButtonGroup } from './RadioButtonGroup'

export default {
  title: '@/design-system/RadioButtonGroup',
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

const collapsedOption = {
  label: 'Option 4',
  name: 'group1',
  description: 'Description 4',
  value: '4',
  collapsed: (
    <div style={{ display: 'flex', flexDirection: 'row', gap: 16 }}>
      <RadioButton name="subchoice" label="Sous-label 1" value="1" />
      <RadioButton name="subchoice" label="Sous-label 2" value="2" />
    </div>
  ),
}

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

export const WithHeadingTagAsTitle: StoryObj<typeof RadioButtonGroup> = {
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Heading Tag as Title',
    labelTag: 'h2',
    options,
  },
}

export const WithSpanTagAsTitle: StoryObj<typeof RadioButtonGroup> = {
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Span Tag as Title',
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

export const WithCommonTag: StoryObj<typeof RadioButtonGroup> = {
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Common Tag',
    variant: 'detailed',
    asset: {
      variant: 'tag',
      tag: {
        label: 'Tag',
        variant: TagVariant.SUCCESS,
      },
    },
    options,
  },
}

export const WithCommonText: StoryObj<typeof RadioButtonGroup> = {
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Common Text',
    variant: 'detailed',
    asset: {
      variant: 'text',
      text: '19€',
    },
    options,
  },
}

export const WithCommonIcon: StoryObj<typeof RadioButtonGroup> = {
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Common Icon',
    variant: 'detailed',
    asset: {
      variant: 'icon',
      src: strokeDateIcon,
    },
    options,
  },
}

export const WithCommonImage: StoryObj<typeof RadioButtonGroup> = {
  args: {
    name: 'radio-button-group',
    label: 'Radio Button Group with Common Image',
    variant: 'detailed',
    asset: {
      variant: 'image',
      src: imageDemo,
      size: 's',
    },
    options,
  },
}

export const WithCollapsed: StoryObj<typeof RadioButtonGroup> = {
  render: () => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    const [checkedOption, setCheckedOption] = useState<string>(
      collapsedOption.value
    )

    return (
      <RadioButtonGroup
        name="radio-button-group"
        label="Radio Button Group with Collapsed Option"
        variant="detailed"
        checkedOption={checkedOption}
        onChange={(e) => setCheckedOption(e.target.value)}
        options={[...options, collapsedOption]}
      />
    )
  },
}
