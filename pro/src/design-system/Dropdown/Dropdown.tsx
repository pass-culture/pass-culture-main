import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import cn from 'classnames'
import React from 'react'
import { Link, type LinkProps } from 'react-router'

import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { Button } from '../Button/Button'
import { Tag, type TagProps } from '../Tag/Tag'
import styles from './Dropdown.module.scss'

// biome-ignore lint/suspicious/noConstEnum: Prefer "const enum": inlines values at compile time, reduces bundle size and avoids runtime objects.
export const enum DropDownItemVariant {
  DESTRUCTIVE = 'destructive',
}

/**
 * Base dropdown props for the component.
 *
 * @typedef {object} BaseProps
 * @property {string} label - Accessible label for the dropdown trigger.
 * @property {'auto' | 'trigger' | number} [width] - Width of the dropdown content. `'auto'` (default), `'trigger'` (match trigger width), or a specific px number.
 * @property {'start' | 'center' | 'end'} [align] - Dropdown alignment relative to the trigger.
 * @property {'top' | 'right' | 'bottom' | 'left'} [side] - Side on which dropdown content appears.
 * @property {React.ReactNode} [trigger] - Custom trigger node (if not provided, a default button is used).
 * @property {boolean} [open] - Controlled open state.
 * @property {(open: boolean) => void} [onOpenChange] - Called when the dropdown open state changes.
 */
type BaseProps = DropdownMenu.DropdownMenuProps & {
  /** Accessible label for the dropdown trigger. */
  label: string
  /** Width of the dropdown content; 'auto' (default), 'trigger' (match trigger width), or a specific px number. */
  width?: 'auto' | 'trigger' | number
  /** Dropdown alignment relative to trigger ('start' | 'center' | 'end'). */
  align?: DropdownMenu.DropdownMenuContentProps['align']
  /** Side for dropdown content ('top', 'right', 'bottom', 'left'). */
  side?: DropdownMenu.DropdownMenuContentProps['side']
  /** Custom trigger node. */
  trigger?: React.ReactNode
  /** Controlled open state. */
  open?: boolean
  /** Callback fired on open state change. */
  onOpenChange?: (open: boolean) => void
}

/**
 * Item definition for dropdown content.
 *
 * @typedef {object} Item
 * @property {string} text - Item display text.
 * @property {ItemLink} [link] - If present, the item becomes a link. Use `opensInNewTab` instead of raw `target`/`rel`: external-link safety (rel + "Nouvelle fenêtre" icon) is then enforced by the component.
 * @property {string} [icon] - Optional icon (either all items have an icon, or none).
 * @property {DropDownItemVariant} [variant] - Variant, e.g. 'destructive'.
 * @property {boolean} [disabled] - Disables the item.
 * @property {TagProps} [tag] - Optional badge/tag to display alongside.
 */

// Use `opensInNewTab` instead of `target`/`rel` to always enforce security and accessibility for external links.
type ItemLink = Omit<LinkProps, 'target' | 'rel'> & {
  /** Opens the link in a new tab, enforcing `rel` + alt text. */
  opensInNewTab?: boolean
}

type Item = DropdownMenu.DropdownMenuItemProps & {
  /** Item display text. */
  text: string
  /** If present, the item becomes a link. */
  link?: ItemLink
  /** Optional icon (all items must include icons if any do). */
  icon?: string
  /** Variant, e.g. 'destructive' for dangerous actions. */
  variant?: DropDownItemVariant
  /** Disabled state. */
  disabled?: boolean
  /** Optional tag/badge element shown next to the item. */
  tag?: TagProps
}

// Items either all have an icon or none at all.
export type DropdownProps =
  | (BaseProps & { items: (Item & { icon: string })[][] })
  | (BaseProps & { items: (Item & { icon?: never })[][] })

export const Dropdown = ({
  label,
  width = 'auto',
  align,
  side,
  trigger,
  open,
  onOpenChange,
  items,
}: Readonly<DropdownProps>): JSX.Element => {
  // When a custom `trigger` is provided we force its `aria-label` *by default*
  // to the `label` prop, so the trigger always exposes an accessible name.
  // A `aria-label` already set on the trigger takes precedence (non-destructive).
  const renderTrigger = (): React.ReactNode => {
    if (!trigger) {
      return <Button type="button" label={label} />
    }

    if (React.isValidElement(trigger)) {
      const { 'aria-label': triggerAriaLabel } = trigger.props as {
        'aria-label'?: string
      }

      return React.cloneElement(trigger, {
        'aria-label': triggerAriaLabel ?? label,
      } as React.HTMLAttributes<HTMLElement>)
    }

    return trigger
  }

  return (
    <DropdownMenu.Root open={open} onOpenChange={onOpenChange}>
      <DropdownMenu.Trigger asChild>{renderTrigger()}</DropdownMenu.Trigger>

      <DropdownMenu.Portal>
        <DropdownMenu.Content
          align={align}
          side={side}
          className={cn(styles['dropdown-content'], {
            [styles['dropdown-width-auto']]: width === 'auto',
            [styles['dropdown-width-trigger']]: width === 'trigger',
          })}
          style={typeof width === 'number' ? { width } : undefined}
        >
          {items.map((itemGroup, index) => (
            <React.Fragment key={itemGroup[0].text}>
              {itemGroup.map(
                ({
                  text,
                  link,
                  icon,
                  variant,
                  disabled,
                  tag,
                  ...itemsProps
                }) => {
                  const opensInNewTab = link?.opensInNewTab ?? false

                  const itemBody = (
                    <>
                      {icon && (
                        <div className={styles['dropdown-item-icon']}>
                          <SvgIcon
                            src={icon}
                            alt={opensInNewTab ? 'Nouvelle fenêtre' : ''}
                          />
                        </div>
                      )}
                      {text}
                      {tag && (
                        <div className={styles['tag-wrapper']}>
                          <Tag {...tag} />
                        </div>
                      )}
                    </>
                  )

                  // Enforce external-link safety with rel="noopener noreferrer"
                  const linkElement = link
                    ? (() => {
                        const {
                          opensInNewTab: _opensInNewTab,
                          ...routerProps
                        } = link

                        return (
                          <Link
                            {...routerProps}
                            target={opensInNewTab ? '_blank' : undefined}
                            rel={
                              opensInNewTab ? 'noopener noreferrer' : undefined
                            }
                          >
                            {itemBody}
                          </Link>
                        )
                      })()
                    : null

                  return (
                    <DropdownMenu.Item
                      {...itemsProps}
                      key={text}
                      disabled={disabled}
                      className={cn(styles['dropdown-item'], {
                        [styles['dropdown-item-disabled']]: disabled,
                        [styles[`dropdown-item-variant-${variant}`]]:
                          variant !== undefined,
                      })}
                      /* If the item is a link, we want the <DropdownMenu.Item> to be rendered as its child : <Link> component */
                      asChild={!!linkElement}
                    >
                      {linkElement ?? itemBody}
                    </DropdownMenu.Item>
                  )
                }
              )}
              {index < items.length - 1 && (
                <DropdownMenu.Separator
                  className={styles['dropdown-item-separator']}
                />
              )}
            </React.Fragment>
          ))}
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  )
}
