import { ListIconButton } from '@/ui-kit/ListIconButton/ListIconButton'

type Action = {
  id: string
  callback: () => void
  label: string
  icon: string
  disabled?: boolean
}

interface Props {
  actions: Action[]
  className?: string
  activationCodeButtonRef?: React.Ref<HTMLButtonElement>
}

export function ActionButtons({
  actions,
  className,
  activationCodeButtonRef,
}: Props) {
  return (
    <div className={className}>
      {actions.map((action) => (
        <ListIconButton
          key={`action-${action.id}`}
          icon={action.icon}
          onClick={action.callback}
          tooltipContent={action.label}
          dataTestid={`action-${action.id}`}
          ref={
            action.label === "Ajouter des codes d'activation"
              ? activationCodeButtonRef
              : undefined
          }
        />
      ))}
    </div>
  )
}
