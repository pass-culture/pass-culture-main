export {}

declare global {
  interface Window {
    hj?: (a: string, b: string) => unknown
    createImageBitmap?: (
      image: ImageBitmapSource,
      options?: ImageBitmapOptions
    ) => Promise<ImageBitmap>

    Beamer: {
      init: () => void
      update: (config: any) => void
      destroy: () => void
      hide: () => void
      show: () => void
    }

    grecaptcha: {
      execute: (siteKey: string, action: { action: string }) => Promise<string>
      ready: (callback: () => void) => void
    }
  }
}
