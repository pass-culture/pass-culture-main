import { useState } from 'react'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant, IconPositionEnum } from '@/design-system/Button/types'
import { Dropdown } from '@/design-system/Dropdown/Dropdown'
import fullDownIcon from '@/icons/full-down.svg'
import fullDownloadIcon from '@/icons/full-download.svg'
import fullUpIcon from '@/icons/full-up.svg'

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

  const [isOpen, setIsOpen] = useState(false)

  return (
    <Dropdown
      label={title ?? label}
      open={isOpen}
      onOpenChange={setIsOpen}
      align="start"
      width="trigger"
      trigger={
        <Button
          label={label}
          variant={ButtonVariant.PRIMARY}
          icon={isOpen ? fullUpIcon : fullDownIcon}
          iconPosition={IconPositionEnum.RIGHT}
          onClick={() => logEvent(logEventName.onToggle)}
          disabled={isDisabled}
        />
      }
      items={[
        [
          {
            text: 'Microsoft Excel (.xls)',
            icon: fullDownloadIcon,
            onClick: () => {
              logEvent(logEventName.onSelectXls)
              onSelect('XLS')
            },
          },
          {
            text: 'Fichier CSV (.csv)',
            icon: fullDownloadIcon,
            onClick: () => {
              logEvent(logEventName.onSelectCsv)
              onSelect('CSV')
            },
          },
        ],
      ]}
    />
  )
}
