declare module '*.module.scss' {
  const classes: { [key: string]: string }
  // biome-ignore lint/style/noDefaultExport: This is a TD file.
  export default classes
}
