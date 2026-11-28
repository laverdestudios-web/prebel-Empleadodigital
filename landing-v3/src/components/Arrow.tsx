/** Flecha ↗ en trazo blanco. size en px de diseño. */
export default function Arrow({ size, className }: { size: number; className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 20 20"
      style={{ width: `calc(${size} * var(--u))`, height: `calc(${size} * var(--u))` }}
      fill="none"
      stroke="currentColor"
      strokeWidth={size > 14 ? 1.6 : 2}
      strokeLinecap="round"
      aria-hidden="true"
    >
      <path d="M4 16 L16 4 M6 4 H16 V14" />
    </svg>
  );
}
