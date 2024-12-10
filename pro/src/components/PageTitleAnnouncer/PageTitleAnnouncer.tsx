export const PageTitleAnnouncer = (): JSX.Element => {
  return (
    <div
      id="page-title-announcer"
      aria-live="assertive"
      className="visually-hidden"
      data-testid="page-title-announcer"
    />
  )
}