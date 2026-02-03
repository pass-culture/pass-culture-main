import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import type { Meta, StoryObj } from '@storybook/react'
import * as React from 'react'

import { DropdownMenuWrapper } from './DropdownMenuWrapper'

// Optionnel si tu veux tester un override d’icône
import fullOtherIcon from '@/icons/full-other.svg'
import { DropdownItem } from './DropdownItem'

const meta: Meta<typeof DropdownMenuWrapper> = {
  title: '@/ui-kit/Dropdown/DropdownMenuWrapper',
  component: DropdownMenuWrapper,
  parameters: { layout: 'centered' },
  args: {
    title: 'Plus d’actions',
    triggerTooltip: true,
  },
}
export default meta

type Story = StoryObj<typeof DropdownMenuWrapper>

export const Default: Story = {
  render: (args) => (
    <DropdownMenuWrapper {...args}>
      <DropdownItem onSelect={() => console.log('Modifier')}>Modifier</DropdownItem>
      <DropdownItem onSelect={() => console.log('Dupliquer')}>
        Dupliquer
      </DropdownItem>
      <DropdownMenu.Separator />
      <DropdownItem onSelect={() => console.log('Supprimer')}>
        Supprimer
      </DropdownItem>
    </DropdownMenuWrapper>
  ),
}

export const WithoutTooltip: Story = {
  args: {
    triggerTooltip: false,
  },
  render: (args) => (
    <DropdownMenuWrapper {...args}>
      <DropdownItem onSelect={() => console.log('Action')}>Action</DropdownItem>
    </DropdownMenuWrapper>
  ),
}

export const WithCustomIcon: Story = {
  args: {
    triggerIcon: fullOtherIcon,
  },
  render: (args) => (
    <DropdownMenuWrapper {...args}>
      <DropdownItem onSelect={() => console.log('Action')}>Action</DropdownItem>
    </DropdownMenuWrapper>
  ),
}

export const WithTriggerRef: Story = {
  render: (args) => {
    const ref = React.useRef<HTMLButtonElement>(null)

    React.useEffect(() => {
      console.log('Trigger button element:', ref.current)
    }, [])

    return (
      <DropdownMenuWrapper {...args} dropdownTriggerRef={ref}>
        <DropdownItem onSelect={() => console.log('Action')}>Action</DropdownItem>
      </DropdownMenuWrapper>
    )
  },
}
