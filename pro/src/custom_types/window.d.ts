export {}

declare global {
  interface Window {
    hj?: (a: string, b: string) => unknown
    createImageBitmap?: (
      image: ImageBitmapSource,
      options?: ImageBitmapOptions
    ) => Promise<ImageBitmap>
  }
}
