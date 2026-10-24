// One label/value row inside a card's <dl className="stats">
export default function Stat({ label, value, hero = false }) {
  return (
    <div className={hero ? 'stat stat-hero' : 'stat'}>
      <dt>{label}</dt>
      <dd>{value}</dd>
    </div>
  )
}
