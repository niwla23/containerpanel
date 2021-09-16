module.exports = {
  purge: [],
  darkMode: false, // or 'media' or 'class'
  theme: {
    extend: {
      animation: {
        'spin-loader': 'spin 2s cubic-bezier(.65,.05,.36,1) infinite',
      }
    },
  },
  variants: {
    extend: {},
  },
  plugins: [],
}
