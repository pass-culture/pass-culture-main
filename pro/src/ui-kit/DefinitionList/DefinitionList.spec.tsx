import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { DefinitionList } from './DefinitionList'

describe('ui-kit:DefinitionList', () => {
  const renderDefinitionList = () =>
    render(
      <DefinitionList>
        <DefinitionList.Row>
          <DefinitionList.Term>Activité</DefinitionList.Term>
          <DefinitionList.Definition>Cinéma</DefinitionList.Definition>
        </DefinitionList.Row>
      </DefinitionList>
    )

  it('should render the terms and definitions without accessibility violations', async () => {
    const { container } = renderDefinitionList()

    expect(container.querySelector('dl')).toBeInTheDocument()
    expect(container.querySelector('dt')).toBeInTheDocument()
    expect(container.querySelector('dd')).toBeInTheDocument()

    expect(screen.getByText(/Activité/)).toBeInTheDocument()
    expect(screen.getByText('Cinéma')).toBeInTheDocument()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should append a colon after each term', () => {
    renderDefinitionList()

    expect(screen.getByText(/Activité/).textContent).toContain(':')
  })
})
