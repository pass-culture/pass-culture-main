import { useState } from 'react'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { useCurrentRoute } from '@/commons/hooks/useCurrentRoute'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant, IconPositionEnum } from '@/design-system/Button/types'
import fullDownIcon from '@/icons/full-down.svg'
import fullDownloadIcon from '@/icons/full-download.svg'
import fullUpIcon from '@/icons/full-up.svg'
import { Dropdown } from '@/ui-kit/Dropdown/Dropdown'
import { DropdownItem } from '@/ui-kit/Dropdown/DropdownItem'

interface DownloadDropdownProps {
  isDisabled?: boolean
  label?: string
  logEventNames: {
    onSelectCsv: string
    onSelectXls: string
    onToggle: string
  }
  onSelect: (type: 'CSV' | 'XLS') => Promise<void>
  title?: string
}
export const DownloadDropdown = ({
  isDisabled = false,
  label = 'Télécharger',
  logEventNames: logEventName,
  onSelect,
  title,
}: Readonly<DownloadDropdownProps>) => {
  const { logEvent } = useAnalytics()
  const currentRoute = useCurrentRoute()

  const [isOpen, setIsOpen] = useState(false)

  return (
    <Dropdown
      title={title ?? label}
      open={isOpen}
      onOpenChange={setIsOpen}
      align="start"
      trigger={
        <Button
          label={label}
          variant={ButtonVariant.PRIMARY}
          icon={isOpen ? fullUpIcon : fullDownIcon}
          iconPosition={IconPositionEnum.RIGHT}
          onClick={() =>
            logEvent(logEventName.onToggle, {
              from: currentRoute.pathname,
            })
          }
          disabled={isDisabled}
        />
      }
    >
      <DropdownItem
        title="Microsoft Excel (.xls)"
        icon={fullDownloadIcon}
        onSelect={() => {
          logEvent(logEventName.onSelectXls, {
            from: currentRoute.pathname,
          })
          onSelect('XLS')
        }}
      />
      <DropdownItem
        title="Fichier CSV (.csv)"
        icon={fullDownloadIcon}
        onSelect={() => {
          logEvent(logEventName.onSelectCsv, {
            from: currentRoute.pathname,
          })
          onSelect('CSV')
        }}
      />
    </Dropdown>
  )
}
