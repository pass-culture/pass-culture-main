export {}

declare global {
  interface Window {
    hj?: (a: string, b: string) => unknown
    createImageBitmap?: (
      image: ImageBitmapSource,
      options?: ImageBitmapOptions
    ) => Promise<ImageBitmap>

    beamer_config: Record<string, unknown>
    Beamer?: {
      init: () => void
      update: (config: any) => void
      destroy: () => void
      hide: () => void
      show: () => void
      config?: Record<string, unknown>
    }

    grecaptcha?: {
      execute: (siteKey: string, action: { action: string }) => Promise<string>
      ready: (callback: () => Promise<void>) => void
      reset?: (siteKey: string) => void
    }
    loadOrejime: (...args: any[]) => void
  }
}
