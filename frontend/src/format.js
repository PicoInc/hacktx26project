// Display-only helpers: the frontend formats money, it never computes it.
// stripIfInteger shows $4,300 for whole amounts and $284.37 when there are cents.
const currency = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  trailingZeroDisplay: 'stripIfInteger',
})
const signedCurrency = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  trailingZeroDisplay: 'stripIfInteger',
  signDisplay: 'exceptZero',
})
const number = new Intl.NumberFormat('en-US')

export const formatCurrency = (n) => currency.format(n)

// "+$4,300" / "−$1,200" (Intl uses a hyphen-minus; swap in a true minus sign)
export const formatSignedCurrency = (n) => signedCurrency.format(n).replace('-', '−')

export const formatNumber = (n) => number.format(n)

export const formatPercent = (n) => `${n}%`
