module.exports = {
  verbose: true,
  setupFiles: ['<rootDir>/.jest-polyfill.js', '<rootDir>/jest.setup.js'],
  testPathIgnorePatterns: ['<rootDir>/.next/', '<rootDir>/node_modules/'],
  modulePaths: ['node_modules', 'src'],
}
