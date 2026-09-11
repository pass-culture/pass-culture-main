import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { InfoPanelList } from './InfoPanelList'
import { InfoPanelSize, InfoPanelSurface, InfoPanelVariant } from './types'

const UNORDERED_PANELS = [
  {
    title: 'Premier panneau',
    description: 'Description du premier panneau',
    icon: 'icon-1.svg',
    iconAlt: 'Icône 1',
  },
  {
    title: 'Second panneau',
    description: 'Description du second panneau',
    icon: 'icon-2.svg',
    iconAlt: 'Icône 2',
  },
]

const ORDERED_PANELS = [
  {
    title: 'Étape 1',
    description: 'Description étape 1',
  },
  {
    title: 'Étape 2',
    description: 'Description étape 2',
  },
]

describe('<InfoPanelList />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = render(
      <InfoPanelList
        variant={InfoPanelVariant.UNORDERED}
        surface={InfoPanelSurface.FLAT}
        panels={UNORDERED_PANELS}
      />
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render an unordered list (ul) with icons when variant is UNORDERED', () => {
    render(
      <InfoPanelList
        variant={InfoPanelVariant.UNORDERED}
        surface={InfoPanelSurface.FLAT}
        panels={UNORDERED_PANELS}
      />
    )

    expect(screen.getByRole('list').tagName).toBe('UL')
    expect(screen.getByRole('img', { name: 'Icône 1' })).toBeInTheDocument()
    expect(screen.getByRole('img', { name: 'Icône 2' })).toBeInTheDocument()
  })

  it('should render an ordered list (ol) with step numbers when variant is ORDERED', () => {
    render(
      <InfoPanelList
        variant={InfoPanelVariant.ORDERED}
        surface={InfoPanelSurface.ELEVATED}
        size={InfoPanelSize.SMALL}
        panels={ORDERED_PANELS}
      />
    )

    expect(screen.getByRole('list').tagName).toBe('OL')
    expect(screen.getByText('1')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { level: 3, name: '1 -Étape 1' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { level: 3, name: '2 -Étape 2' })
    ).toBeInTheDocument()
  })

  it('should render h2 headings when titleLevel is "2"', () => {
    render(
      <InfoPanelList
        variant={InfoPanelVariant.UNORDERED}
        surface={InfoPanelSurface.FLAT}
        titleLevel="2"
        panels={UNORDERED_PANELS}
      />
    )

    expect(
      screen.getByRole('heading', { level: 2, name: 'Premier panneau' })
    ).toBeInTheDocument()
  })

  it('should render panel descriptions', () => {
    render(
      <InfoPanelList
        variant={InfoPanelVariant.UNORDERED}
        surface={InfoPanelSurface.FLAT}
        panels={UNORDERED_PANELS}
      />
    )

    expect(
      screen.getByText('Description du premier panneau')
    ).toBeInTheDocument()
    expect(
      screen.getByText('Description du second panneau')
    ).toBeInTheDocument()
  })
})
