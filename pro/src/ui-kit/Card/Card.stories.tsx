import type { Meta, StoryObj } from '@storybook/react-vite'

import { Card } from './Card'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonSize, ButtonVariant } from '@/design-system/Button/types'

import sampleImage from './assets/sample-image-landscape.jpg'

const meta: Meta<typeof Card> = {
  title: '@/ui-kit/Card',
  component: Card,
}

export default meta
type Story = StoryObj<typeof Card>

export const Default: Story = {
  render: () => (
    <Card>
      <Card.Header
        title="Titre de la carte"
        subtitle="Sous-titre de la carte"
      />
      <Card.Content>
        <p>Contenu de la carte avec des informations utiles.</p>
      </Card.Content>
      <Card.Footer>
        <Button label="Action principale" />
      </Card.Footer>
    </Card>
  ),
}

export const WithImage: Story = {
  render: () => (
    <Card>
      <Card.Image src={sampleImage} alt="Image d'exemple" />
      <Card.Header
        title="Carte avec image"
        subtitle="L'image a des valeurs par défaut"
      />
      <Card.Content>
        <p>Le composant Card.Image gère automatiquement les dimensions et le border-radius.</p>
      </Card.Content>
      <Card.Footer>
        <Button label="En savoir plus" />
      </Card.Footer>
    </Card>
  ),
}

export const InfoVariant: Story = {
  render: () => (
    <Card variant="info">
      <Card.Header
        title="Carte avec variant info"
      />
      <Card.Content>
        <p>
          Le variant "info" utilise un fond coloré et un bouton transparent
          pour mettre en avant du contenu important.
        </p>
      </Card.Content>
      <Card.Footer>
        <Button as="a" to="#" isExternal opensInNewTab label="En savoir plus" size={ButtonSize.SMALL} variant={ButtonVariant.SECONDARY} color={ButtonColor.NEUTRAL} transparent/>
      </Card.Footer>
    </Card>
  ),
}

export const WithoutSubtitle: Story = {
  render: () => (
    <Card>
      <Card.Header title="Carte sans sous-titre" />
      <Card.Content>
        <p>Cette carte n'a pas de sous-titre.</p>
      </Card.Content>
    </Card>
  ),
}

export const WithCustomTitleTag: Story = {
  render: () => (
    <Card>
      <Card.Header title="Titre en h3" titleTag="h3" />
      <Card.Content>
        <p>Le titre utilise une balise h3 au lieu du h2 par défaut.</p>
      </Card.Content>
    </Card>
  ),
}

export const SideBySide: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '24px' }}>
      <Card>
        <Card.Header title="Carte 1" subtitle="Première carte" />
        <Card.Content>
          <p>Contenu de la première carte.</p>
        </Card.Content>
        <Card.Footer>
          <Button label="Action 1" />
        </Card.Footer>
      </Card>
      <Card>
        <Card.Header title="Carte 2" subtitle="Deuxième carte" />
        <Card.Content>
          <p>Contenu de la deuxième carte.</p>
        </Card.Content>
        <Card.Footer>
          <Button label="Action 2" variant={ButtonVariant.SECONDARY}/>
        </Card.Footer>
      </Card>
    </div>
  ),
}
