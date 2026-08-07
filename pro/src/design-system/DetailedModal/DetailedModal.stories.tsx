import type { Meta, StoryObj } from '@storybook/react-vite'
import { useState } from 'react'
import { withRouter } from 'storybook-addon-remix-react-router'

import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullBackIcon from '@/icons/full-back.svg'

import { DetailedModal, type DetailedModalProps } from './DetailedModal'
import { TextInput } from '../TextInput/TextInput'

const DetailedModalWithOpenButton = (args: DetailedModalProps) => {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div style={{ minHeight: '240px' }}>
      <Button
        variant={ButtonVariant.PRIMARY}
        label="Ouvrir la modal"
        onClick={() => setIsOpen(true)}
      />

      <DetailedModal
        {...args}
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
      />
    </div>
  )
}

const meta: Meta<typeof DetailedModal> = {
  title: '@/design-system/DetailedModal',
  component: DetailedModal,
  args: {
    isOpen: true,
    onClose: () => {},
    title:
      'Titre très très très loong Titre très très très loongTitre très très très loong',
    description:
      'Ceci est une description qui peut être assez longue en fonction du contenu de la page. Il n’y a pas de limites en termes de nombre de lignes…',
    onGoBack: () => {},
    primaryAction: <Button variant={ButtonVariant.PRIMARY} label="Primary" />,
    secondaryAction: (
      <Button
        variant={ButtonVariant.SECONDARY}
        color={ButtonColor.NEUTRAL}
        label="Secondary"
      />
    ),
    tertiaryAction: (
      <Button
        variant={ButtonVariant.TERTIARY}
        color={ButtonColor.NEUTRAL}
        label="Tertiary"
      />
    ),
    footerMessage: 'Message précisant le bouton',
    children: (
      <form onSubmit={(e) => e.preventDefault()}>
        <div style={{ display: 'grid', gap: '12px' }}>
          <TextInput label="Nom de l’offre" name="name" />
          <span>
            Lorem ipsum dolor sit amet consectetur adipisicing elit. Repellendus
            ut quo velit soluta esse est omnis, laudantium sapiente sint
            molestiae illum, autem magni! Reiciendis exercitationem inventore
            praesentium sunt ut recusandae? Lorem ipsum dolor sit amet
            consectetur adipisicing elit. Repellendus ut quo velit soluta esse
            est omnis, laudantium sapiente sint molestiae illum, autem magni!
            Reiciendis exercitationem inventore praesentium sunt ut recusandae?
            Lorem ipsum dolor sit amet consectetur adipisicing elit. Repellendus
            ut quo velit soluta esse est omnis, laudantium sapiente sint
            molestiae illum, autem magni! Reiciendis exercitationem inventore
            praesentium sunt ut recusandae?
          </span>
        </div>
      </form>
    ),
  },
}

export default meta

type Story = StoryObj<typeof DetailedModal>

export const Default: Story = {
  args: {
    goBackButtonAriaLabel: '',
    isFooterFixed: false,
  },

  render: (args) => <DetailedModalWithOpenButton {...args} />,
}

export const WithoutGoBack: Story = {
  args: {
    onGoBack: undefined,
  },
}

export const WithLongDescription: Story = {
  args: {
    description:
      'Ceci est une description qui peut être assez longue en fonction du contenu de la page. Il n’y a pas de limites en termes de nombre de lignes. Ceci est une description qui peut être assez longue en fonction du contenu de la page. Il n’y a pas de limites en termes de nombre de lignes. Ceci est une description qui peut être assez longue en fonction du contenu de la page. Il n’y a pas de limites en termes de nombre de lignes. mottresssssloooooongsansespacespourtesterlewrappingresponsivemottresssssloooooongsansespacespourtesterlewrappingresponsive.',
    isFooterFixed: false,
  },
}

export const WithLoadingActions: Story = {
  args: {
    primaryAction: (
      <Button variant={ButtonVariant.PRIMARY} label="Primary" isLoading />
    ),
    secondaryAction: (
      <Button
        variant={ButtonVariant.SECONDARY}
        color={ButtonColor.NEUTRAL}
        label="Secondary"
        disabled
      />
    ),
  },
}

export const WithFixedFooter: Story = {
  args: {
    isFooterFixed: true,
    children: (
      <div style={{ display: 'grid', gap: '12px' }}>
        {Array.from({ length: 20 }).map((_, index) => {
          const lineNumber = index + 1
          return (
            <p key={`content-line-${lineNumber}`}>
              Ligne de contenu {lineNumber}
            </p>
          )
        })}
      </div>
    ),
  },
}

export const WithLinkAndIconActions: Story = {
  decorators: [withRouter],
  args: {
    tertiaryAction: (
      <Button
        as="router-link"
        to="/offres"
        variant={ButtonVariant.TERTIARY}
        color={ButtonColor.NEUTRAL}
        label="Voir les offres"
        icon={fullBackIcon}
      />
    ),
    secondaryAction: (
      <Button
        variant={ButtonVariant.SECONDARY}
        color={ButtonColor.NEUTRAL}
        label="Secondary"
        icon={fullBackIcon}
      />
    ),
    primaryAction: <Button variant={ButtonVariant.PRIMARY} label="Primary" />,
  },
}

export const LoadingVariant: Story = {
  args: {
    loadingState: {
      label: 'Chargement en cours…',
    },
    children: <div />,
  },
  render: (args) => <DetailedModalWithOpenButton {...args} />,
}

export const WithSingleAction: Story = {
  args: {
    primaryAction: <Button variant={ButtonVariant.PRIMARY} label="Primary" />,
    secondaryAction: undefined,
    tertiaryAction: undefined,
    footerMessage: undefined,
  },
}

const steps = [
  {
    title: 'Étape 1 - Informations générales',
    description: 'Renseignez les informations de base de votre offre.',
    content: <TextInput label="Nom de l'offre" name="name" />,
  },
  {
    title: 'Étape 2 - Détails',
    description: 'Ajoutez les détails complémentaires.',
    content: <TextInput label="Description" name="description" />,
  },
  {
    title: 'Étape 3 - Confirmation',
    description: 'Vérifiez et confirmez les informations saisies.',
    content: <p>Tout est correct ? Cliquez sur "Terminer" pour valider.</p>,
  },
]

const DetailedModalWithSteps = () => {
  const [isOpen, setIsOpen] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)

  const isLastStep = currentStep === steps.length - 1
  const isFirstStep = currentStep === 0
  const step = steps[currentStep]

  const handleClose = () => {
    setIsOpen(false)
    setCurrentStep(0)
  }

  return (
    <div style={{ minHeight: '240px' }}>
      <Button
        variant={ButtonVariant.PRIMARY}
        label="Ouvrir la modal"
        onClick={() => setIsOpen(true)}
      />
      <DetailedModal
        isOpen={isOpen}
        onClose={handleClose}
        title={step.title}
        description={step.description}
        onGoBack={isFirstStep ? undefined : () => setCurrentStep((s) => s - 1)}
        primaryAction={
          <Button
            variant={ButtonVariant.PRIMARY}
            label={isLastStep ? 'Terminer' : 'Suivant'}
            onClick={
              isLastStep ? handleClose : () => setCurrentStep((s) => s + 1)
            }
          />
        }
        secondaryAction={
          <Button
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            label="Annuler"
            onClick={handleClose}
          />
        }
        footerMessage={`Étape ${currentStep + 1} sur ${steps.length}`}
      >
        <form onSubmit={(e) => e.preventDefault()}>
          <div style={{ display: 'grid', gap: '12px' }}>{step.content}</div>
        </form>
      </DetailedModal>
    </div>
  )
}

export const WithStepNavigation: Story = {
  render: () => <DetailedModalWithSteps />,
}
