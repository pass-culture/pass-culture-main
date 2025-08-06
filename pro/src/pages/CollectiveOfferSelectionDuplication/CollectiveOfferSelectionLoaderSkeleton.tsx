import { Skeleton } from '@/ui-kit/Skeleton/Skeleton'

export const SkeletonLoader = () => {
  const bigSkeletonCount = 6

  return (
    <div data-testid="skeleton-loader">
      <Skeleton height="1rem" width="30%" />
      {Array.from({ length: bigSkeletonCount }).map((_, i) => (
        <Skeleton key={i} height="5rem" width="100%" />
      ))}
    </div>
  )
}
