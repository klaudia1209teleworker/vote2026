export function getCandidateKey(c: {
  county: string;
  position: string;
  district?: string | null;
  name: string;
  number?: number | null;
}): string {
  const district = c.district || c.county;
  return `${c.county}|${c.position}|${district}|${c.name}|${c.number ?? ''}`;
}
