import { AccessibleDate } from '@/ui-kit/AccessibleDate/AccessibleDate'

type HighlightDatespanTagProps = {
  highlightDatespan: Array<string>
}

export function HighlightDatespanTag({
  highlightDatespan,
}: HighlightDatespanTagProps): React.ReactNode {
  if (highlightDatespan[0] === highlightDatespan[1]) {
    return <AccessibleDate date={highlightDatespan[0]} />
  }

  return (
    <>
      <AccessibleDate date={highlightDatespan[0]} />
      au
      <AccessibleDate date={highlightDatespan[1]} />
    </>
  )
}
