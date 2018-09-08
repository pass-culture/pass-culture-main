module.exports = {
  testEnvironment: 'node',
  testMatch: ['**/?(*.)+(spec).js?(x)'],
  testURL: 'http://localhost',
  transform: {
    '^.+\\.js$': 'babel-jest',
  },
  transformIgnorePatterns: [
    '<rootDir>/node_modules/',
    '[/\\\\]node_modules[/\\\\].+\\.(js|jsx|mjs)$',
  ],
  verbose: false,
}
