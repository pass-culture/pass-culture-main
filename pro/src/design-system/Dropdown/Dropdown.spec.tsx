import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import fullLinkIcon from '@/icons/full-link.svg'

import { TagVariant } from '../Tag/Tag'
import { DropDownItemVariant, Dropdown, type DropdownProps } from './Dropdown'

const defaultItems: DropdownProps['items'] = [
  [{ text: 'Item 1' }, { text: 'Item 2' }],
]

// The component renders `react-router` <Link> for link items and a design-system
// <Button> as the default trigger, both of which need router/redux context, so
// every test goes through `renderWithProviders`.
function renderDropdown(props?: Partial<DropdownProps>) {
  const mergedProps = {
    label: 'Dropdown',
    items: defaultItems,
    ...props,
  } as DropdownProps

  return renderWithProviders(<Dropdown {...mergedProps} />)
}

// Opens the menu and returns the trigger, factored out because almost every
// assertion needs the (portaled) content to be mounted first.
async function openDropdown(triggerName = 'Dropdown') {
  const trigger = screen.getByRole('button', { name: triggerName })
  await userEvent.click(trigger)
  return trigger
}

describe('<Dropdown />', () => {
  describe('happy path', () => {
    it('should render the default trigger button labelled with the `label` prop', () => {
      renderDropdown()

      expect(
        screen.getByRole('button', { name: 'Dropdown' })
      ).toBeInTheDocument()
    })

    it('should keep the menu closed until the trigger is clicked', () => {
      renderDropdown()

      expect(screen.queryByRole('menuitem')).not.toBeInTheDocument()
    })

    it('should open the menu and reveal items when the trigger is clicked', async () => {
      renderDropdown()

      await openDropdown()

      expect(
        screen.getByRole('menuitem', { name: 'Item 1' })
      ).toBeInTheDocument()
      expect(
        screen.getByRole('menuitem', { name: 'Item 2' })
      ).toBeInTheDocument()
    })

    it('should fire the item `onSelect` handler when an item is clicked', async () => {
      const onSelect = vi.fn()
      renderDropdown({
        items: [[{ text: 'Item 1', onSelect }, { text: 'Item 2' }]],
      })

      await openDropdown()
      await userEvent.click(screen.getByRole('menuitem', { name: 'Item 1' }))

      expect(onSelect).toHaveBeenCalledOnce()
    })

    it('should render an icon for each item when `icon` is provided', async () => {
      renderDropdown({
        items: [
          [
            { text: 'Item 1', icon: fullLinkIcon },
            { text: 'Item 2', icon: fullLinkIcon },
          ],
        ],
      })

      await openDropdown()

      // The icon is rendered as a decorative (aria-hidden) <svg> pointing at the
      // provided sprite via <use xlink:href="...#icon">.
      const item = screen.getByRole('menuitem', { name: 'Item 1' })
      const svg = item.querySelector('svg')
      expect(svg).toBeInTheDocument()
      expect(svg).toHaveAttribute('aria-hidden', 'true')
      expect(item.querySelector('use')).toHaveAttribute(
        'xlink:href',
        `${fullLinkIcon}#icon`
      )
    })

    it('should render a tag alongside an item when `tag` is provided', async () => {
      renderDropdown({
        items: [
          [{ text: 'Item 1', tag: { label: 'New', variant: TagVariant.NEW } }],
        ],
      })

      await openDropdown()

      expect(screen.getByText('New')).toBeInTheDocument()
    })

    it('should render a separator between item groups', async () => {
      const { container } = renderDropdown({
        items: [[{ text: 'Item 1' }], [{ text: 'Item 2' }]],
      })

      await openDropdown()

      expect(
        container.ownerDocument.querySelector('[role="separator"]')
      ).toBeInTheDocument()
    })

    it('should NOT render a separator for a single group', async () => {
      const { container } = renderDropdown({ items: [[{ text: 'Item 1' }]] })

      await openDropdown()

      expect(
        container.ownerDocument.querySelector('[role="separator"]')
      ).not.toBeInTheDocument()
    })

    it('should render an item as a link when `link` is provided', async () => {
      renderDropdown({
        items: [[{ text: 'Go', link: { to: '/somewhere' } }]],
      })

      await openDropdown()

      const link = screen.getByRole('menuitem', { name: 'Go' })
      expect(link.tagName).toBe('A')
      expect(link).toHaveAttribute('href', '/somewhere')
    })

    it('should not set `target`/`rel` for an internal link', async () => {
      renderDropdown({
        items: [[{ text: 'Go', link: { to: '/somewhere' } }]],
      })

      await openDropdown()

      const link = screen.getByRole('menuitem', { name: 'Go' })
      expect(link).not.toHaveAttribute('target')
      expect(link).not.toHaveAttribute('rel')
    })

    it('should enforce `target`, `rel` and "Nouvelle fenêtre" on icon when `opensInNewTab` is set', async () => {
      renderDropdown({
        items: [
          [
            {
              text: 'External',
              icon: fullLinkIcon,
              link: { to: '/out', opensInNewTab: true },
            },
          ],
        ],
      })

      await openDropdown()

      // The accessible name combines the text and the injected icon's alt, so
      // the user is warned the link opens a new tab (WCAG 3.2.5).
      const link = screen.getByRole('menuitem', {
        name: 'Nouvelle fenêtre External',
      })
      expect(link).toHaveAttribute('target', '_blank')
      // Security/privacy guard cannot be forgotten by the caller.
      expect(link).toHaveAttribute('rel', 'noopener noreferrer')
      expect(
        screen.getByRole('img', { name: 'Nouvelle fenêtre' })
      ).toBeInTheDocument()
    })

    it('should use a custom trigger instead of the default button', () => {
      renderDropdown({
        label: 'Accessible name',
        trigger: <button type="button">Custom content</button>,
      })

      // The custom node is rendered (its visible text is present) in place of the
      // default design-system <Button>, which would have rendered the label text.
      expect(screen.getByText('Custom content')).toBeInTheDocument()
    })

    it('should fall back the custom trigger `aria-label` to the `label` prop', () => {
      renderDropdown({
        label: 'Accessible name',
        trigger: <button type="button">Icon</button>,
      })

      // The custom trigger has no aria-label, so the component injects `label` as
      // the accessible name while keeping its own visible content.
      expect(
        screen.getByRole('button', { name: 'Accessible name' })
      ).toBeInTheDocument()
      expect(screen.getByText('Icon')).toBeInTheDocument()
    })

    it('should keep an explicit `aria-label` on the custom trigger (precedence)', () => {
      renderDropdown({
        label: 'Fallback label',
        trigger: (
          <button type="button" aria-label="Own label">
            Icon
          </button>
        ),
      })

      expect(
        screen.getByRole('button', { name: 'Own label' })
      ).toBeInTheDocument()
      expect(
        screen.queryByRole('button', { name: 'Fallback label' })
      ).not.toBeInTheDocument()
    })

    it('should call `onOpenChange` when the open state changes', async () => {
      const onOpenChange = vi.fn()
      renderDropdown({ onOpenChange })

      await openDropdown()

      expect(onOpenChange).toHaveBeenCalledWith(true)
    })

    it('should respect the controlled `open` prop', () => {
      renderDropdown({ open: true })

      expect(
        screen.getByRole('menuitem', { name: 'Item 1' })
      ).toBeInTheDocument()
    })

    it('should not open on click when controlled `open` is false', async () => {
      const onOpenChange = vi.fn()
      renderDropdown({ open: false, onOpenChange })

      await openDropdown()

      // In controlled mode the parent owns the state: the menu stays closed
      // until `open` is flipped, even though `onOpenChange` is requested.
      expect(screen.queryByRole('menuitem')).not.toBeInTheDocument()
      expect(onOpenChange).toHaveBeenCalledWith(true)
    })

    it('should disable an item flagged as `disabled`', async () => {
      const onSelect = vi.fn()
      renderDropdown({
        items: [[{ text: 'Item 1', disabled: true, onSelect }]],
      })

      await openDropdown()

      const item = screen.getByRole('menuitem', { name: 'Item 1' })
      expect(item).toHaveAttribute('data-disabled')
    })

    it('should apply the destructive variant class to an item', async () => {
      renderDropdown({
        items: [[{ text: 'Delete', variant: DropDownItemVariant.DESTRUCTIVE }]],
      })

      await openDropdown()

      expect(screen.getByRole('menuitem', { name: 'Delete' })).toHaveClass(
        'dropdown-item-variant-destructive'
      )
    })
  })

  describe('width prop', () => {
    it('should apply the auto-width class by default', async () => {
      renderDropdown()

      await openDropdown()

      expect(screen.getByRole('menu')).toHaveClass('dropdown-width-auto')
    })

    it('should apply the trigger-width class when `width="trigger"`', async () => {
      renderDropdown({ width: 'trigger' })

      await openDropdown()

      expect(screen.getByRole('menu')).toHaveClass('dropdown-width-trigger')
    })

    it('should apply an inline pixel width when `width` is a number', async () => {
      renderDropdown({ width: 200 })

      await openDropdown()

      const menu = screen.getByRole('menu')
      expect(menu).toHaveStyle({ width: '200px' })
      // A numeric width must not also set the auto/trigger modifier classes.
      expect(menu).not.toHaveClass('dropdown-width-auto')
      expect(menu).not.toHaveClass('dropdown-width-trigger')
    })
  })

  describe('edge cases', () => {
    it('should render the trigger but no items for an empty `items` array', async () => {
      renderDropdown({ items: [] })

      await openDropdown()

      expect(screen.queryByRole('menuitem')).not.toBeInTheDocument()
    })

    it('should handle `width` of 0 as an inline pixel width', async () => {
      renderDropdown({ width: 0 })

      await openDropdown()

      const menu = screen.getByRole('menu')
      // 0 is a valid number, so the inline style branch is taken (not the classes).
      expect(menu).not.toHaveClass('dropdown-width-auto')
      expect(menu).not.toHaveClass('dropdown-width-trigger')
    })
  })

  describe('error cases', () => {
    // These render with the bare `render()` (no router error boundary) so the
    // synchronous render error propagates and can be asserted with `toThrow`.
    // `console.error` is silenced because React logs the error before rethrowing,
    // which would otherwise trip `vitest-fail-on-console`.
    it('should throw when a group is empty (no item to derive the key from)', () => {
      // `items.map` reads `itemGroup[0].text` for the React key; an empty group
      // makes `itemGroup[0]` undefined, which throws at render time.
      vi.spyOn(console, 'error').mockImplementation(() => {})

      // Cast through the whole props object: an empty group does not satisfy the
      // discriminated `items` union, which is exactly the invalid input under test.
      const invalidProps = {
        label: 'Dropdown',
        open: true,
        items: [[]],
      } as unknown as DropdownProps

      expect(() => render(<Dropdown {...invalidProps} />)).toThrow()
    })

    it('should throw when `trigger` is a non-element node (string)', () => {
      // `DropdownMenu.Trigger` uses `asChild`, which slots onto a single React
      // element. A plain string cannot be slotted, so rendering throws. This
      // documents that the `return trigger` fallback for non-elements is unusable.
      vi.spyOn(console, 'error').mockImplementation(() => {})

      expect(() =>
        render(
          <Dropdown
            label="Dropdown"
            trigger="Plain text trigger"
            items={defaultItems}
          />
        )
      ).toThrow()
    })
  })

  it('should render without accessibility violations (closed)', async () => {
    const { container } = renderDropdown()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render without accessibility violations (open)', async () => {
    const { baseElement } = renderDropdown()

    // Open via a real click so the state update is wrapped in `act`, then run
    // axe on `baseElement` to cover the portaled menu. The `region` rule is
    // disabled because the menu is portaled outside any landmark in test
    // isolation (it lives inside page landmarks in the real app).
    await openDropdown()

    expect(
      await axe(baseElement, { rules: { region: { enabled: false } } })
    ).toHaveNoViolations()
  })
})
