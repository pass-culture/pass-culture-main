import type { Meta, StoryObj } from '@storybook/react'
import * as React from 'react'

import { Dropdown } from './Dropdown'

import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import { DropdownItem } from './DropdownItem'

const meta: Meta<typeof Dropdown> = {
  title: '@/ui-kit/Dropdown',
  component: Dropdown,
  parameters: { layout: 'centered' },
  args: {
    align: 'end',
  },
}
export default meta

type Story = StoryObj<typeof Dropdown>

export const WithChildren: Story = {
  args: {
    trigger: <Button label="Ouvrir" variant={ButtonVariant.PRIMARY} />,
  },
  render: (args) => (
    <Dropdown {...args}>
      <DropdownItem onSelect={() => console.log('Profil')}>Profil</DropdownItem>
      <DropdownItem onSelect={() => console.log('Paramètres')}>
        Paramètres
      </DropdownItem>

      <DropdownItem onSelect={() => console.log('Déconnexion')}>
        Déconnexion
      </DropdownItem>
    </Dropdown>
  ),
}

export const WithOptions: Story = {
  args: {
    title: "dropdown",
    trigger: <Button label="Options (API simple)" variant={ButtonVariant.PRIMARY} />,
  },
  render: (args) => <Dropdown {...args} >
      <DropdownItem onSelect= {() => console.log('Profil') }>Profil</DropdownItem>
      <DropdownItem onSelect={ () => console.log('Paramètres') }>Paramètres</DropdownItem>
      <DropdownItem onSelect= {() => console.log('Déconnexion') }>Déconnexion</DropdownItem>
  </Dropdown>,
}


export const ControlledOpen: Story = {
  args: {
    trigger: <Button label="Controlled" variant={ButtonVariant.PRIMARY} />,
  },
  render: (args) => {
    const [open, setOpen] = React.useState(false)

    return (
        <Dropdown
          {...args}
          open={open}
          onOpenChange={setOpen}
        >
          <DropdownItem onSelect= {() => console.log('A')}>Action A</DropdownItem>
          <DropdownItem onSelect= {() => console.log('B')}>Action B</DropdownItem>
        </Dropdown>
    )
  },
}

export const LongContent: Story = {
  args: {
    trigger: <Button label="Long content" variant={ButtonVariant.PRIMARY} />,
    contentClassName: 'storybookDropdownLong',
  },
  render: (args) => <Dropdown {...args} >
    {Array.from({ length: 20 }).map((_,item) => (
        <DropdownItem key={`Action ${item + 1}`} onSelect= { () => console.log(`Action ${item + 1}`)}> 
        {`Action ${item + 1}`}
        </DropdownItem>
    ))}
  </Dropdown>,
}
