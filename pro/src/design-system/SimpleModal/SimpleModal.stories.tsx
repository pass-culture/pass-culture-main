import { Meta, StoryObj } from "@storybook/react-vite"
import { SimpleModal } from "./SimpleModal"

import fullNextIcon from '@/icons/full-next.svg'
import fullClearIcon from '@/icons/full-clear.svg'
import { Button } from "../Button/Button"
import { ButtonColor, ButtonVariant } from "../Button/types"
import { useState } from "react"


const SimpleModalWithOpenButton = (
  args: React.ComponentProps<typeof SimpleModal>
) => {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div style={{ minHeight: '240px' }}>
      <Button
        variant={ButtonVariant.PRIMARY}
        label="Ouvrir la modale simple"
        onClick={() => setIsOpen(true)}
      />

      <SimpleModal
        {...args}
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
      />
    </div>
  )
}


const meta: Meta<typeof SimpleModal> = {
  title: '@/design-system/SimpleModal',
  component: SimpleModal,
}


export default meta
type Story = StoryObj<typeof SimpleModal>

export const Default: Story = {
  render: () => <SimpleModalWithOpenButton title={"Titre très très très loong"} isOpen={true} iconPath={fullNextIcon} onClose={() => {}} actionButtons={
  <>
    <Button label="Annuler" variant={ButtonVariant.TERTIARY} color={ButtonColor.NEUTRAL} icon={fullClearIcon}/>
    <Button label="Annuler" variant={ButtonVariant.SECONDARY}/>
    <Button label="Confirmer" variant={ButtonVariant.PRIMARY}/>
  </>
  }>
    <p style={{ textAlign: 'center' }}>Description de 2 à 3 lignes max Description de 2 à 3 lignes max Description de 2 à 3 lignes max</p>
  </SimpleModalWithOpenButton>,
}
