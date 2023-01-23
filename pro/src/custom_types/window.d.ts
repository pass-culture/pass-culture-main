export {}

declare global {
  interface Window {
    hj?: (a: string, b: string) => unknown
  }
}
