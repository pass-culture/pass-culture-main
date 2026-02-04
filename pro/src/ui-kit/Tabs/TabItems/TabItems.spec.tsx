import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { TabItems } from './TabItems'

const renderTabItems = (handleChange = () => {}) =>
  render(
    <div>
      <TabItems
        selectedKey="individual"
        tabs={[
          {
            label: 'Individuelles',
            key: 'individual',
          },
          {
            label: 'Collectives',
            key: 'collective',
          },
        ]}
        onChange={handleChange}
        navLabel={'Onglets - tabs mode'}
      />
      <div id="panel-individual" role="tabpanel"></div>
      <div id="panel-collective" role="tabpanel"></div>
    </div>
  )

describe('TabItems', () => {
  it('should render without accessibility violation', async () => {
    const { container } = renderTabItems()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render two tabs', () => {
    renderTabItems()

    expect(screen.getAllByRole('tab')).toHaveLength(2)
    expect(screen.getByRole('tab', { selected: true })).toHaveTextContent(
      'Individuelles'
    )
    expect(screen.getByRole('tab', { selected: false })).toHaveTextContent(
      'Collectives'
    )
  })

  it('should have working tabs', async () => {
    const user = userEvent.setup()
    const handleClickMock = vi.fn()
    renderTabItems(handleClickMock)

    expect(screen.getByRole('tab', { selected: true })).toHaveTextContent(
      'Individuelles'
    )

    await user.click(screen.getByRole('tab', { name: /Collectives/ }))
    expect(handleClickMock).toHaveBeenCalledWith('collective')
  })
})
