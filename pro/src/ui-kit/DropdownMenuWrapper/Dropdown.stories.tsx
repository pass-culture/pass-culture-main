import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import type { Meta, StoryObj } from '@storybook/react'
import * as React from 'react'

import { Dropdown } from './Dropdown'

// Adapte si ton Button est ailleurs / props différentes
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import { DropdownItem } from './DropdownItem'

const meta: Meta<typeof Dropdown> = {
  title: '@/ui-kit/Dropdown/Dropdown',
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

      {/* Tu peux utiliser aussi les primitives Radix si besoin */}
      <DropdownMenu.Separator />

      <DropdownItem onSelect={() => console.log('Déconnexion')}>
        Déconnexion
      </DropdownItem>
    </Dropdown>
  ),
}

export const WithOptions: Story = {
  args: {
    trigger: <Button label="Options (API simple)" variant={ButtonVariant.PRIMARY} />,
    options: [
      { id: 'profile', element: 'Profil', onSelect: () => console.log('Profil') },
      { id: 'settings', element: 'Paramètres', onSelect: () => console.log('Paramètres') },
      { id: 'logout', element: 'Déconnexion', onSelect: () => console.log('Déconnexion') },
    ],
  },
  render: (args) => <Dropdown {...args} />,
}

export const ControlledOpen: Story = {
  args: {
    trigger: <Button label="Controlled" variant={ButtonVariant.PRIMARY} />,
  },
  render: (args) => {
    const [open, setOpen] = React.useState(false)

    return (
      <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
        <Dropdown
          {...args}
          open={open}
          onOpenChange={setOpen}
          options={[
            { id: 'a', element: 'Action A', onSelect: () => console.log('A') },
            { id: 'b', element: 'Action B', onSelect: () => console.log('B') },
          ]}
        />

        <Button
          label={open ? 'Fermer le menu' : 'Ouvrir le menu'}
          variant={ButtonVariant.SECONDARY}
          onClick={() => setOpen((v) => !v)}
        />
      </div>
    )
  },
}

export const LongContent: Story = {
  args: {
    trigger: <Button label="Long content" variant={ButtonVariant.PRIMARY} />,
    contentClassName: 'storybookDropdownLong',
    options: Array.from({ length: 20 }).map((_, i) => ({
      id: String(i),
      element: `Action ${i + 1}`,
      onSelect: () => console.log(`Action ${i + 1}`),
    })),
  },
  render: (args) => <Dropdown {...args} />,
}
